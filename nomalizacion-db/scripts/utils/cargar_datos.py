# -*- coding: utf-8 -*-
import os
import sys
import time
import psycopg2

# Obtener la raíz del proyecto (2 niveles arriba si estás en utils/, o 1 si estás en raíz)
def get_project_root():
    """Encuentra la raíz del proyecto buscando una carpeta 'output_csv' o 'docker-compose.yml'"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Subir hasta encontrar una carpeta con 'output_csv' o hasta llegar a /
    while current_dir != '/':
        if os.path.exists(os.path.join(current_dir, 'output_csv')):
            return current_dir
        if os.path.exists(os.path.join(current_dir, 'docker-compose.yml')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # Si no encuentra, asumir que output_csv está en el mismo nivel que el script
    return os.path.dirname(os.path.abspath(__file__))

# Configuración
PROJECT_ROOT = get_project_root()
CSV_DIR = os.path.join(PROJECT_ROOT, 'output_csv')

# Para debugging (opcional, eliminar en producción)
print(f"[DEBUG] Proyecto raíz: {PROJECT_ROOT}")
print(f"[DEBUG] Buscando CSVs en: {CSV_DIR}")

DB_URL = "postgresql://postgres:postgres@db:5432/hospital_db"  # Usar 'db' como host en Docker

ORDEN_IMPORTACION = [
    ("cat_especialidades", "cat_especialidades.csv"),
    ("cat_aseguradoras", "cat_aseguradoras.csv"),
    ("cat_habitaciones", "cat_habitaciones.csv"),
    ("cat_medicamentos", "cat_medicamentos.csv"),
    ("medicos", "medicos.csv"),
    ("pacientes", "pacientes.csv"),
    ("citas_medicas", "citas_medicas.csv"),
    ("ingresos_hospitalarios", "ingresos_hospitalarios.csv"),
    ("historiales_clinicos", "historiales_clinicos.csv"),
    ("recetas_medicas", "recetas_medicas.csv"),
    ("detalles_recetas", "detalles_recetas.csv")
]

def cargar_datos():
    # Verificar que la carpeta output_csv existe
    if not os.path.exists(CSV_DIR):
        print(f"[!] ERROR: No se encuentra la carpeta '{CSV_DIR}'")
        print(f"[!] Asegúrate de que los CSV estén generados en output_csv/")
        sys.exit(1)
    
    try:
        print("[*] Conectando a hospital_db...")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SET client_min_messages TO WARNING;")
        
        tiempo_inicio = time.time()
        
        for tabla, archivo in ORDEN_IMPORTACION:
            ruta = os.path.join(CSV_DIR, archivo)
            if not os.path.exists(ruta):
                print(f"[!] ADVERTENCIA: No se encuentra {archivo}, se omite {tabla}")
                continue
                
            print(f"[*] Inyectando '{archivo}' en tabla '{tabla}'...")
            t_tabla = time.time()
            
            # Usar utf-8-sig para eliminar posible BOM
            with open(ruta, 'r', encoding='utf-8-sig') as f:
                # Leer el header dinámico para evitar chocar con la llave primaria generada
                header = f.readline().strip()
                f.seek(0)  # Regresar al inicio del archivo
                
                sql_copy = f"COPY {tabla} ({header}) FROM STDIN WITH CSV HEADER NULL AS '';"
                cursor.copy_expert(sql_copy, f)
                
            print(f"    -> [OK] Tiempo: {time.time() - t_tabla:.4f}s")
            
        conn.commit()
        print(f"\n[!] CARGA MASIVA COMPLETADA en {time.time() - tiempo_inicio:.2f} segundos.")
        
    except Exception as e:
        print(f"\n[❌] ERROR CRÍTICO: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    cargar_datos()