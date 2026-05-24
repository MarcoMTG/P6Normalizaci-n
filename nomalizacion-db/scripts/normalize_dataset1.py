# -*- coding: utf-8 -*-
"""
normalize_dataset_netflix.py
============================
Normaliza netflix_titles.csv a 3FN y genera CSVs listos para PostgreSQL.
Corregido: evita que enteros se escriban como "1.0".
"""

import os
import re
import argparse
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración de rutas (igual que el hospital, pero para Netflix)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)          # raíz del proyecto
DEFAULT_CSV = os.path.join(BASE_DIR, 'datos', 'netflix_titles.csv')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'output_csv')

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Normaliza el CSV de Netflix a 3FN.')
parser.add_argument('--input',  default=DEFAULT_CSV, help='Ruta al CSV original')
parser.add_argument('--limit',  type=int, default=None, help='Límite de filas (None = todas)')
args = parser.parse_args()

ARCHIVO_ORIGEN   = args.input
LIMITE_REGISTROS = args.limit

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def limpiar_nombre(nombre: str) -> str:
    return re.sub(r'\s+', ' ', nombre).strip()

def split_multivalor(valor) -> list[str]:
    if pd.isna(valor) or str(valor).strip() == '':
        return []
    return [limpiar_nombre(v) for v in str(valor).split(',') if limpiar_nombre(v)]

def parsear_fecha(valor) -> str | None:
    if pd.isna(valor) or str(valor).strip() == '':
        return None
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(str(valor).strip(), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def parsear_duracion(valor) -> tuple[int | None, str | None]:
    if pd.isna(valor) or str(valor).strip() == '':
        return None, None
    partes = str(valor).strip().split()
    if len(partes) >= 2:
        try:
            num = int(partes[0])
            unidad = partes[1].lower()
            if unidad.startswith('min'):
                unidad = 'min'
            elif unidad == 'season':
                unidad = 'Season'
            elif unidad == 'seasons':
                unidad = 'Seasons'
            else:
                unidad = unidad.capitalize()
            return num, unidad
        except ValueError:
            pass
    return None, None

# ===========================================================================
# LECTURA
# ===========================================================================
print(f"[*] Leyendo CSV: {ARCHIVO_ORIGEN}")
if not os.path.exists(ARCHIVO_ORIGEN):
    raise FileNotFoundError(f"No se encontró el archivo: {ARCHIVO_ORIGEN}")

df_raw = pd.read_csv(ARCHIVO_ORIGEN, nrows=LIMITE_REGISTROS, low_memory=False)
df = df_raw.dropna(subset=['show_id']).copy().reset_index(drop=True)
print(f"    → {len(df)} filas válidas cargadas.")

# ===========================================================================
# NIVEL 0: CATÁLOGOS
# ===========================================================================
print("\n[*] Nivel 0 — Generando catálogos...")

# cat_tipos_contenido
tipos_unicos = df['type'].dropna().unique()
cat_tipos = pd.DataFrame({
    'id_tipo':      range(1, len(tipos_unicos) + 1),
    'nombre_tipo':  tipos_unicos,
    'descripcion':  ['Película' if t == 'Movie' else 'Serie de TV' for t in tipos_unicos]
})
cat_tipos.to_csv(f"{OUTPUT_DIR}/cat_tipos_contenido.csv", index=False)
print(f"    cat_tipos_contenido:  {len(cat_tipos)} registros")
dict_tipos = dict(zip(cat_tipos['nombre_tipo'], cat_tipos['id_tipo']))

# cat_clasificaciones
ratings_unicos = df['rating'].dropna().unique()
desc_rating = {
    'G': 'General Audiences', 'PG': 'Parental Guidance', 'PG-13': 'Parents Cautioned',
    'R': 'Restricted', 'NC-17': 'Adults Only', 'TV-Y': 'All Children', 'TV-Y7': 'Older Children',
    'TV-G': 'General Audience', 'TV-PG': 'Parental Guidance', 'TV-14': 'Parents Strongly Cautioned',
    'TV-MA': 'Mature Audience', 'NR': 'Not Rated', 'UR': 'Unrated'
}
cat_clasificaciones = pd.DataFrame({
    'id_clasificacion': range(1, len(ratings_unicos) + 1),
    'codigo': ratings_unicos,
    'descripcion': [desc_rating.get(r, 'Sin descripción') for r in ratings_unicos]
})
cat_clasificaciones.to_csv(f"{OUTPUT_DIR}/cat_clasificaciones.csv", index=False)
print(f"    cat_clasificaciones:  {len(cat_clasificaciones)} registros")
dict_clasificaciones = dict(zip(cat_clasificaciones['codigo'], cat_clasificaciones['id_clasificacion']))

# cat_generos
todos_generos = set()
for val in df['listed_in'].dropna():
    for g in split_multivalor(val):
        todos_generos.add(g)
cat_generos = pd.DataFrame({
    'id_genero': range(1, len(todos_generos) + 1),
    'nombre': sorted(todos_generos)
})
cat_generos.to_csv(f"{OUTPUT_DIR}/cat_generos.csv", index=False)
print(f"    cat_generos:          {len(cat_generos)} registros")
dict_generos = dict(zip(cat_generos['nombre'], cat_generos['id_genero']))

# cat_paises
todos_paises = set()
for val in df['country'].dropna():
    for p in split_multivalor(val):
        todos_paises.add(p)
cat_paises = pd.DataFrame({
    'id_pais': range(1, len(todos_paises) + 1),
    'nombre': sorted(todos_paises)
})
cat_paises.to_csv(f"{OUTPUT_DIR}/cat_paises.csv", index=False)
print(f"    cat_paises:           {len(cat_paises)} registros")
dict_paises = dict(zip(cat_paises['nombre'], cat_paises['id_pais']))

# ===========================================================================
# NIVEL 1: PERSONAS
# ===========================================================================
print("\n[*] Nivel 1 — Generando personas...")
todas_personas = set()
for col in ['director', 'cast']:
    for val in df[col].dropna():
        for p in split_multivalor(val):
            todas_personas.add(p)
personas = pd.DataFrame({
    'id_persona': range(1, len(todas_personas) + 1),
    'nombre_completo': sorted(todas_personas)
})
personas.to_csv(f"{OUTPUT_DIR}/personas.csv", index=False)
print(f"    personas:             {len(personas)} registros")
dict_personas = dict(zip(personas['nombre_completo'], personas['id_persona']))

# ===========================================================================
# NIVEL 2: TÍTULOS
# ===========================================================================
print("\n[*] Nivel 2 — Generando titulos...")
filas_titulos = []
for _, row in df.iterrows():
    dur_val, dur_unidad = parsear_duracion(row.get('duration'))
    filas_titulos.append({
        'show_id':          str(row['show_id']).strip(),
        'id_tipo':          dict_tipos.get(str(row['type']).strip()) if not pd.isna(row.get('type')) else None,
        'id_clasificacion': dict_clasificaciones.get(str(row['rating']).strip()) if not pd.isna(row.get('rating')) else None,
        'titulo':           str(row['title']).strip() if not pd.isna(row.get('title')) else 'Sin título',
        'fecha_agregado':   parsear_fecha(row.get('date_added')),
        'anio_estreno':     int(row['release_year']) if not pd.isna(row.get('release_year')) else None,
        'duracion_valor':   dur_val,
        'duracion_unidad':  dur_unidad,
        'descripcion':      str(row['description']).strip() if not pd.isna(row.get('description')) else None,
    })
titulos = pd.DataFrame(filas_titulos)

# *** CORRECCIÓN CLAVE: convertir columnas enteras a Int64 (nullable) ***
columnas_int = ['id_tipo', 'id_clasificacion', 'anio_estreno', 'duracion_valor']
for col in columnas_int:
    if col in titulos.columns:
        titulos[col] = pd.to_numeric(titulos[col], errors='coerce').astype('Int64')

# Insertar id_titulo (serial)
titulos.insert(0, 'id_titulo', range(1, len(titulos) + 1))
titulos.to_csv(f"{OUTPUT_DIR}/titulos.csv", index=False)
print(f"    titulos:              {len(titulos)} registros")
dict_titulos = dict(zip(titulos['show_id'], titulos['id_titulo']))

# ===========================================================================
# NIVEL 3: ASOCIACIONES N:M
# ===========================================================================
print("\n[*] Nivel 3 — Generando tablas de asociación...")

# titulo_directores
rows_dir = []
for _, row in df.iterrows():
    id_t = dict_titulos.get(str(row['show_id']).strip())
    for nombre in split_multivalor(row.get('director')):
        id_p = dict_personas.get(nombre)
        if id_t and id_p:
            rows_dir.append({'id_titulo': id_t, 'id_persona': id_p})
pd.DataFrame(rows_dir).drop_duplicates().to_csv(f"{OUTPUT_DIR}/titulo_directores.csv", index=False)
print(f"    titulo_directores:    {len(rows_dir)} registros")

# titulo_actores
rows_act = []
for _, row in df.iterrows():
    id_t = dict_titulos.get(str(row['show_id']).strip())
    for orden, nombre in enumerate(split_multivalor(row.get('cast')), start=1):
        id_p = dict_personas.get(nombre)
        if id_t and id_p:
            rows_act.append({'id_titulo': id_t, 'id_persona': id_p, 'orden_credito': orden})
df_act = pd.DataFrame(rows_act).drop_duplicates(subset=['id_titulo','id_persona'])
# Asegurar que orden_credito sea entero
df_act['orden_credito'] = pd.to_numeric(df_act['orden_credito'], errors='coerce').astype('Int64')
df_act.to_csv(f"{OUTPUT_DIR}/titulo_actores.csv", index=False)
print(f"    titulo_actores:       {len(df_act)} registros")

# titulo_paises
rows_pais = []
for _, row in df.iterrows():
    id_t = dict_titulos.get(str(row['show_id']).strip())
    paises = split_multivalor(row.get('country'))
    for i, nombre in enumerate(paises):
        id_p = dict_paises.get(nombre)
        if id_t and id_p:
            rows_pais.append({'id_titulo': id_t, 'id_pais': id_p, 'es_primario': (i == 0)})
pd.DataFrame(rows_pais).drop_duplicates(subset=['id_titulo','id_pais']).to_csv(f"{OUTPUT_DIR}/titulo_paises.csv", index=False)
print(f"    titulo_paises:        {len(rows_pais)} registros")

# titulo_generos
rows_gen = []
for _, row in df.iterrows():
    id_t = dict_titulos.get(str(row['show_id']).strip())
    for nombre in split_multivalor(row.get('listed_in')):
        id_g = dict_generos.get(nombre)
        if id_t and id_g:
            rows_gen.append({'id_titulo': id_t, 'id_genero': id_g})
pd.DataFrame(rows_gen).drop_duplicates().to_csv(f"{OUTPUT_DIR}/titulo_generos.csv", index=False)
print(f"    titulo_generos:       {len(rows_gen)} registros")

# ===========================================================================
# RESUMEN FINAL
# ===========================================================================
archivos = [
    'cat_tipos_contenido.csv', 'cat_clasificaciones.csv',
    'cat_paises.csv', 'cat_generos.csv',
    'personas.csv',
    'titulos.csv',
    'titulo_directores.csv', 'titulo_actores.csv',
    'titulo_paises.csv', 'titulo_generos.csv',
]
print(f"\n{'='*60}")
print(f"  NORMALIZACIÓN COMPLETADA — {len(archivos)} archivos en '{OUTPUT_DIR}/'")
print(f"{'='*60}")
for arch in archivos:
    ruta = os.path.join(OUTPUT_DIR, arch)
    if os.path.exists(ruta):
        n = max(0, sum(1 for _ in open(ruta)) - 1)
        print(f"  ✓  {arch:<35} {n:>5} filas")
    else:
        print(f"  ✗  {arch:<35} NO GENERADO")
print(f"{'='*60}\n")