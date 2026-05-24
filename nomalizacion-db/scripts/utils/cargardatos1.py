import os
import sys
import time
import psycopg2


# ---------------------------------------------------------------------------
# Localización automática del directorio raíz del proyecto
# ---------------------------------------------------------------------------
def get_project_root() -> str:
    """Sube en el árbol de directorios hasta encontrar 'output_csv' o el raíz del proyecto."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current != os.path.sep:
        if os.path.exists(os.path.join(current, 'output_csv')):
            return current
        if os.path.exists(os.path.join(current, 'docker-compose.yml')):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.abspath(__file__))


PROJECT_ROOT = get_project_root()
CSV_DIR      = os.path.join(PROJECT_ROOT, 'output_csv')

print(f"[DEBUG] Proyecto raíz : {PROJECT_ROOT}")
print(f"[DEBUG] CSVs en       : {CSV_DIR}")

# ---------------------------------------------------------------------------
# Configuración de conexión
# Lee de variables de entorno (Docker) o usa defaults para desarrollo local.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'port':     int(os.environ.get('DB_PORT', '5435')),    # Puerto externo del docker-compose
    'dbname':   os.environ.get('DB_NAME',     'netflix_db'),
    'user':     os.environ.get('DB_USER',     'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
}

# ---------------------------------------------------------------------------
# Orden de importación: tabla → archivo CSV
# ¡El orden es crítico! Las FK deben existir antes que los hijos.
# ---------------------------------------------------------------------------
ORDEN_IMPORTACION = [
    # Nivel 0 — Catálogos (sin dependencias externas)
    ('cat_tipos_contenido',  'cat_tipos_contenido.csv'),
    ('cat_clasificaciones',  'cat_clasificaciones.csv'),
    ('cat_paises',           'cat_paises.csv'),
    ('cat_generos',          'cat_generos.csv'),
    # Nivel 1 — Entidades maestras
    ('personas',             'personas.csv'),
    # Nivel 2 — Transaccionales
    ('titulos',              'titulos.csv'),
    # Nivel 3 — Asociaciones N:M
    ('titulo_directores',    'titulo_directores.csv'),
    ('titulo_actores',       'titulo_actores.csv'),
    ('titulo_paises',        'titulo_paises.csv'),
    ('titulo_generos',       'titulo_generos.csv'),
]


# ---------------------------------------------------------------------------
# Función principal de carga
# ---------------------------------------------------------------------------
def cargar_datos():
    # Verificar directorio de CSVs
    if not os.path.exists(CSV_DIR):
        print(f"[!] ERROR: No se encuentra el directorio '{CSV_DIR}'.")
        print("     Ejecuta primero normalize_dataset_netflix.py para generar los CSV.")
        sys.exit(1)

    conn   = None
    cursor = None

    try:
        print(f"\n[*] Conectando a {DB_CONFIG['dbname']} en {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False          # Transacción explícita para rollback total en error
        cursor = conn.cursor()

        # Suprimir NOTICEs de PostgreSQL en la salida
        cursor.execute("SET client_min_messages TO WARNING;")

        # Deshabilitar triggers y FK checks durante la carga masiva para mayor velocidad
        # (seguro porque el orden de importación ya garantiza integridad referencial)
        cursor.execute("SET session_replication_role = replica;")

        tiempo_inicio = time.time()
        total_filas   = 0

        print(f"[*] Iniciando carga masiva de {len(ORDEN_IMPORTACION)} tablas...\n")
        print(f"  {'Tabla':<30} {'Archivo':<35} {'Filas':>7}  {'Tiempo':>8}")
        print(f"  {'-'*30} {'-'*35} {'-'*7}  {'-'*8}")

        for tabla, archivo in ORDEN_IMPORTACION:
            ruta = os.path.join(CSV_DIR, archivo)

            if not os.path.exists(ruta):
                print(f"  [!] ADVERTENCIA: '{archivo}' no encontrado — se omite '{tabla}'.")
                continue

            t_inicio_tabla = time.time()

            # Contar filas (sin header) para reporte
            with open(ruta, 'r', encoding='utf-8-sig') as f_count:
                n_filas = sum(1 for _ in f_count) - 1

            with open(ruta, 'r', encoding='utf-8-sig') as f:
                # Leer header dinámico para mapear exactamente las columnas del CSV
                # (excluye columnas seriales que PostgreSQL autogenera)
                header = f.readline().strip()
                f.seek(0)

                sql_copy = (
                    f"COPY {tabla} ({header}) "
                    f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '', ENCODING 'UTF8');"
                )
                cursor.copy_expert(sql_copy, f)

            elapsed = time.time() - t_inicio_tabla
            total_filas += n_filas
            print(f"  ✓  {tabla:<30} {archivo:<35} {n_filas:>7}  {elapsed:>7.3f}s")

        # Rehabilitar FK checks y hacer commit
        cursor.execute("SET session_replication_role = DEFAULT;")
        conn.commit()

        elapsed_total = time.time() - tiempo_inicio
        print(f"\n{'='*85}")
        print(f"  CARGA COMPLETADA — {total_filas} filas en {len(ORDEN_IMPORTACION)} tablas  "
              f"({elapsed_total:.2f}s total)")
        print(f"{'='*85}\n")

    except psycopg2.OperationalError as e:
        print(f"\nERROR DE CONEXIÓN: {e}")
        print(f"     Verifica que el contenedor 'db_netflix' esté corriendo y que el puerto "
              f"{DB_CONFIG['port']} esté expuesto.")
        sys.exit(1)

    except psycopg2.Error as e:
        print(f"\n ERROR DE BASE DE DATOS: {e}")
        if conn:
            conn.rollback()
            print("     Se realizó ROLLBACK completo. La base de datos está sin cambios.")
        sys.exit(1)

    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("[*] Conexión cerrada.")


# ---------------------------------------------------------------------------
# Verificación de integridad post-carga (opcional, para debugging)
# ---------------------------------------------------------------------------
def verificar_integridad():
    """Ejecuta conteos rápidos en cada tabla y los imprime."""
    try:
        conn   = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("\n[*] Verificación de integridad post-carga:")
        tablas = [t for t, _ in ORDEN_IMPORTACION]
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
            count = cursor.fetchone()[0]
            print(f"    {tabla:<30} → {count:>6} filas")

        # Verificar vista plana
        cursor.execute("SELECT COUNT(*) FROM v_titulos_planos;")
        print(f"    {'v_titulos_planos':<30} → {cursor.fetchone()[0]:>6} filas (vista)")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[!] No se pudo verificar integridad: {e}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    cargar_datos()
    verificar_integridad()