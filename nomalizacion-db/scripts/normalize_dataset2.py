"""
normalize_dataset2.py
=====================
Normalización del Dataset 2: E-commerce Sales Data

Flujo completo con Docker:
  1. Carga data.csv → tabla ecommerce_raw (desnormalizada) en PostgreSQL
  2. Aplica 1FN, 2FN, 3FN
  3. Genera 5 tablas normalizadas en PostgreSQL:
       countries, customers, products, invoices, invoice_items
  4. Exporta CSV y SQLite como respaldo local

Flujo sin Docker:
  1. Lee data.csv directamente
  2. Genera CSV normalizados + SQLite en data/normalized/ecommerce/
"""

import os, sys, time
import pandas as pd
import sqlite3

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV   = os.path.join(BASE_DIR, "data", "raw", "data.csv")
OUT_DIR   = os.path.join(BASE_DIR, "data", "normalized", "ecommerce")
DB_PATH   = os.path.join(OUT_DIR,  "ecommerce_3fn.db")
DDL_PATH  = os.path.join(BASE_DIR, "sql", "ddl", "dataset2_schema.sql")
DML_PATH  = os.path.join(BASE_DIR, "sql", "dml", "dataset2_data.sql")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
from utils import limpiar_dataframe, exportar_csv, reporte_redundancia

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DDL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(DML_PATH), exist_ok=True)

# ── Detectar modo Docker ───────────────────────────────────────────────────
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
USAR_POSTGRES = POSTGRES_HOST is not None

if USAR_POSTGRES:
    from sqlalchemy import create_engine, text
    PG_USER = os.environ.get("POSTGRES_USER", "practica6")
    PG_PASS = os.environ.get("POSTGRES_PASSWORD", "practica6pass")
    PG_DB   = os.environ.get("POSTGRES_DB",   "ecommerce_3fn")
    PG_PORT = os.environ.get("POSTGRES_PORT", "5432")
    PG_URL  = f"postgresql://{PG_USER}:{PG_PASS}@{POSTGRES_HOST}:{PG_PORT}/{PG_DB}"

    # Esperar a que PostgreSQL esté listo
    print("[Docker] Esperando a PostgreSQL...")
    for intento in range(15):
        try:
            engine = create_engine(PG_URL)
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
            print("[Docker] PostgreSQL listo.")
            break
        except Exception:
            time.sleep(3)
    else:
        print("[Docker] No se pudo conectar a PostgreSQL. Saliendo.")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# 1. CARGA DEL CSV → tabla desnormalizada (ecommerce_raw)
# ══════════════════════════════════════════════════════════════════════════
print("\n[1/5] Cargando dataset original...")
df = pd.read_csv(RAW_CSV, encoding="latin-1", dtype=str)
df = limpiar_dataframe(df)
df.columns = ["invoice_no", "stock_code", "description",
              "quantity", "invoice_date", "unit_price",
              "customer_id", "country"]

print(f"     Filas totales   : {len(df):,}")

df["quantity"]     = pd.to_numeric(df["quantity"],    errors="coerce")
df["unit_price"]   = pd.to_numeric(df["unit_price"],  errors="coerce")
df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

if USAR_POSTGRES:
    print("[Docker] Cargando tabla desnormalizada ecommerce_raw en PostgreSQL...")
    with engine.begin() as con:
        df.to_sql("ecommerce_raw", con, if_exists="replace", index=False)
    print(f"[Docker] ecommerce_raw cargada: {len(df):,} filas")

# Limpiar filas sin CustomerID para normalizar
df_clean = df.dropna(subset=["customer_id"]).copy()
df_clean["customer_id"] = df_clean["customer_id"].apply(lambda x: int(float(x)))
print(f"     Filas válidas   : {len(df_clean):,} (sin NaN en customer_id)")


# ══════════════════════════════════════════════════════════════════════════
# 2. PRIMERA FORMA NORMAL (1FN)
# ══════════════════════════════════════════════════════════════════════════
print("\n[2/5] 1FN — verificando atomicidad...")
print(f"     Registros únicos (invoice_no, stock_code): "
      f"{df_clean.drop_duplicates(['invoice_no','stock_code']).shape[0]:,}")


# ══════════════════════════════════════════════════════════════════════════
# 3. SEGUNDA FORMA NORMAL (2FN) — eliminar dependencias parciales
# ══════════════════════════════════════════════════════════════════════════
print("\n[3/5] 2FN — eliminando dependencias parciales...")

products = (
    df_clean.groupby("stock_code")["description"]
    .agg(lambda x: x.mode()[0] if not x.mode().empty else None)
    .reset_index()
)
print(f"     products       : {len(products):,} filas")

invoices_raw = (
    df_clean[["invoice_no", "customer_id", "invoice_date", "country"]]
    .drop_duplicates(subset=["invoice_no"])
    .copy()
)
print(f"     invoices (raw) : {len(invoices_raw):,} filas")

invoice_items = df_clean[["invoice_no", "stock_code", "quantity", "unit_price"]].copy()
invoice_items.insert(0, "item_id", range(1, len(invoice_items) + 1))
print(f"     invoice_items  : {len(invoice_items):,} filas")


# ══════════════════════════════════════════════════════════════════════════
# 4. TERCERA FORMA NORMAL (3FN) — eliminar dependencias transitivas
# ══════════════════════════════════════════════════════════════════════════
print("\n[4/5] 3FN — eliminando dependencias transitivas...")

country_list = sorted(df_clean["country"].dropna().unique())
countries = pd.DataFrame({
    "country_id":   range(1, len(country_list) + 1),
    "country_name": country_list
})
country_map = dict(zip(countries["country_name"], countries["country_id"]))
print(f"     countries      : {len(countries):,} filas")

cust_country = (
    df_clean[["customer_id", "country"]]
    .drop_duplicates(subset=["customer_id"])
    .copy()
)
cust_country["country_id"] = cust_country["country"].map(country_map)
customers = cust_country[["customer_id", "country_id"]].copy()
print(f"     customers      : {len(customers):,} filas")

invoices = invoices_raw[["invoice_no", "customer_id", "invoice_date"]].copy()
invoices["invoice_date"] = invoices["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
print(f"     invoices       : {len(invoices):,} filas")


# ══════════════════════════════════════════════════════════════════════════
# 5. EXPORTACIÓN
# ══════════════════════════════════════════════════════════════════════════
print("\n[5/5] Exportando resultados...")

tablas = {
    "countries":     countries,
    "customers":     customers,
    "products":      products,
    "invoices":      invoices,
    "invoice_items": invoice_items,
}

# ── CSV individuales (siempre) ─────────────────────────────────────────────
for nombre, tabla in tablas.items():
    exportar_csv(tabla, OUT_DIR, nombre)

# ── SQLite (siempre, como respaldo local) ──────────────────────────────────
conn = sqlite3.connect(DB_PATH)
for nombre, tabla in tablas.items():
    tabla.to_sql(nombre, conn, if_exists="replace", index=False)
conn.close()
print(f"[SQLite] DB guardada en: {DB_PATH}")

# ── PostgreSQL: cargar las 5 tablas normalizadas ───────────────────────────
if USAR_POSTGRES:
    print("\n[PostgreSQL] Cargando tablas normalizadas en orden (respetando FKs)...")
    orden = ["countries", "customers", "products", "invoices", "invoice_items"]
    with engine.begin() as con:
        con.execute(text("SET session_replication_role = replica;"))
        for nombre in orden:
            tablas[nombre].to_sql(nombre, con, if_exists="replace", index=False)
            print(f"  [PG] {nombre}: {len(tablas[nombre]):,} filas")
        con.execute(text("SET session_replication_role = DEFAULT;"))
    print("[PostgreSQL] ✅ Tablas normalizadas cargadas correctamente")

# ── Reporte final ──────────────────────────────────────────────────────────
reporte_redundancia(df, tablas)
print("\n✅ Normalización completada exitosamente.")
