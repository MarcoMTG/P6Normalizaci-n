# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime, timedelta

# Obtener la ruta base (donde está la carpeta scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /home/uri/Documents/DATASETS/scripts
BASE_DIR = os.path.dirname(SCRIPT_DIR)       

ARCHIVO_ORIGEN = os.path.join(BASE_DIR, 'datos', 'dataset.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output_csv')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Aplica tus niveles de prueba directo aquí (50, 5000, 100000)
LIMITE_REGISTROS = 5000

print(f"[*] Leyendo el dataset original (Límite: {LIMITE_REGISTROS} filas)...")
print(f"[*] Ruta del archivo: {ARCHIVO_ORIGEN}")

print(f"[DEBUG] __file__ es: {__file__}")
print(f"[DEBUG] Ruta absoluta del script: {os.path.abspath(__file__)}")
print(f"[DEBUG] SCRIPT_DIR: {SCRIPT_DIR}")
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] ARCHIVO_ORIGEN completo: {ARCHIVO_ORIGEN}")

# Listar qué hay en BASE_DIR para verificar
if os.path.exists(BASE_DIR):
    print(f"[DEBUG] Contenido de {BASE_DIR}:")
    for item in os.listdir(BASE_DIR):
        print(f"  - {item}")

if not os.path.exists(ARCHIVO_ORIGEN):
    print(f"[!] ERROR: No se encuentra el archivo en {ARCHIVO_ORIGEN}")
    print(f"[!] Verifica que la ruta sea correcta")
    exit(1)

df = pd.read_csv(ARCHIVO_ORIGEN, nrows=LIMITE_REGISTROS, low_memory=False)

# Limpieza básica para emparejar con las restricciones CHECK del SQL
df['gender'] = df['gender'].fillna('O').map({'M': 'M', 'F': 'F'}).fillna('O')
df['age'] = df['age'].fillna(40).astype(int)
df['apache_3j_bodysystem'] = df['apache_3j_bodysystem'].fillna('Medicina General')
df['icu_admit_source'] = df['icu_admit_source'].fillna('Particular')
df['icu_id'] = df['icu_id'].fillna(999).astype(int)

# =====================================================================
# 1. CATÁLOGOS (Nivel 0)
# =====================================================================
print("[*] Procesando Catálogos...")

cat_esp = df[['apache_3j_bodysystem']].drop_duplicates().reset_index(drop=True)
cat_esp.index += 1
cat_esp.columns = ['nombre_especialidad']
cat_esp.to_csv(f"{OUTPUT_DIR}/cat_especialidades.csv", index=False)

cat_aseg = df[['icu_admit_source']].drop_duplicates().reset_index(drop=True)
cat_aseg.index += 1
cat_aseg.columns = ['nombre_aseguradora']
cat_aseg['telefono_contacto'] = '555-000-0000'
cat_aseg.to_csv(f"{OUTPUT_DIR}/cat_aseguradoras.csv", index=False)

cat_hab = df[['icu_id']].drop_duplicates().reset_index(drop=True)
cat_hab.index += 1
cat_hab['numero_habitacion'] = 'Hab-' + cat_hab['icu_id'].astype(str)
cat_hab['tipo_habitacion'] = 'UCI' # Forzado a UCI por el constraint del SQL
cat_hab['estado_habitacion'] = 'Ocupada'
cat_hab[['numero_habitacion', 'tipo_habitacion', 'estado_habitacion']].to_csv(f"{OUTPUT_DIR}/cat_habitaciones.csv", index=False)

meds_data = {
    'nombre_comercial': ['Paracetamol', 'Ibuprofeno', 'Omeprazol', 'Amoxicilina'],
    'componente_actico': ['Paracetamol', 'Ibuprofeno', 'Omeprazol', 'Amoxicilina'],
    'presentacion': ['Tabletas 500mg', 'Cápsulas 400mg', 'Cápsulas 20mg', 'Suspensión']
}
cat_med = pd.DataFrame(meds_data)
cat_med.index += 1
cat_med.to_csv(f"{OUTPUT_DIR}/cat_medicamentos.csv", index=False)

# =====================================================================
# 2. ENTIDADES MAESTRAS (Nivel 1)
# =====================================================================
print("[*] Generando maestros (Médicos y Pacientes)...")

df_meds = df[['hospital_id', 'apache_3j_bodysystem']].drop_duplicates('hospital_id').reset_index(drop=True)
df_meds.index += 1
df_meds['nombre'] = 'Médico'
df_meds['apellido'] = 'Hosp_' + df_meds['hospital_id'].astype(str)
df_meds['cedula_profesional'] = 'CED-' + df_meds['hospital_id'].astype(str)
dict_esp = {k: v for v, k in zip(cat_esp.index, cat_esp['nombre_especialidad'])}
df_meds['id_especialidad'] = df_meds['apache_3j_bodysystem'].map(dict_esp)
df_meds['telefono'] = '555-123-4567'
df_meds['email'] = 'med_' + df_meds['hospital_id'].astype(str) + '@hospital.com'
df_meds[['nombre', 'apellido', 'cedula_profesional', 'id_especialidad', 'telefono', 'email']].to_csv(f"{OUTPUT_DIR}/medicos.csv", index=False)

df_pacs = df[['patient_id', 'age', 'gender', 'icu_admit_source']].drop_duplicates('patient_id').reset_index(drop=True)
df_pacs.index += 1
df_pacs['nombre'] = 'Paciente'
df_pacs['apellido'] = 'ID_' + df_pacs['patient_id'].astype(str)
current_year = 2026
df_pacs['fecha_nacimiento'] = (current_year - df_pacs['age']).astype(str) + '-01-01'
df_pacs['telefono'] = '555-987-6543'
df_pacs['email'] = 'paciente_' + df_pacs['patient_id'].astype(str) + '@mail.com'
dict_aseg = {k: v for v, k in zip(cat_aseg.index, cat_aseg['nombre_aseguradora'])}
df_pacs['id_aseguradora'] = df_pacs['icu_admit_source'].map(dict_aseg)
df_pacs['nss_seguro'] = 'NSS-' + df_pacs['patient_id'].astype(str)
df_pacs[['nombre', 'apellido', 'fecha_nacimiento', 'gender', 'telefono', 'email', 'id_aseguradora', 'nss_seguro']].rename(columns={'gender': 'genero'}).to_csv(f"{OUTPUT_DIR}/pacientes.csv", index=False)

# =====================================================================
# 3. TRANSACCIONALES (Niveles 2 y 3)
# =====================================================================
print("[*] Generando transacciones (Citas, Ingresos, Historiales)...")

df_trans = df[['encounter_id', 'patient_id', 'hospital_id', 'icu_id', 'apache_3j_bodysystem', 'pre_icu_los_days']].copy()
dict_pacs = {k: v for v, k in zip(df_pacs.index, df_pacs['patient_id'])}
dict_meds = {k: v for v, k in zip(df_meds.index, df_meds['hospital_id'])}
dict_habs = {k: v for v, k in zip(cat_hab.index, cat_hab['icu_id'])}

df_trans['id_paciente'] = df_trans['patient_id'].map(dict_pacs)
df_trans['id_medico'] = df_trans['hospital_id'].map(dict_meds)
df_trans['id_habitacion'] = df_trans['icu_id'].map(dict_habs)
base_date = datetime.now() - timedelta(days=30)
df_trans['fecha_base'] = base_date.strftime('%Y-%m-%d %H:%M:%S')

df_citas = df_trans[['id_paciente', 'id_medico']].copy()
df_citas['fecha_hora'] = df_trans['fecha_base']
df_citas['motivo_consulta'] = 'Evaluación inicial UCI'
df_citas['estado_cita'] = 'Completada'
df_citas.to_csv(f"{OUTPUT_DIR}/citas_medicas.csv", index=False)

df_ingresos = df_trans[['id_paciente', 'id_habitacion']].copy()
df_ingresos['fecha_ingreso'] = df_trans['fecha_base']
df_ingresos['fecha_alta'] = ''
df_ingresos['motivo_ingreso'] = df_trans['apache_3j_bodysystem']
df_ingresos.to_csv(f"{OUTPUT_DIR}/ingresos_hospitalarios.csv", index=False)

df_historial = df_trans[['id_paciente', 'id_medico']].copy()
df_historial['fecha_registro'] = df_trans['fecha_base']
df_historial['sintomas'] = 'Síntomas de ' + df_trans['apache_3j_bodysystem']
df_historial['diagnostico'] = 'Diagnóstico APACHE: ' + df_trans['apache_3j_bodysystem']
df_historial.to_csv(f"{OUTPUT_DIR}/historiales_clinicos.csv", index=False)

df_recetas = pd.DataFrame({'id_historial': range(1, len(df_historial) + 1)})
df_recetas['fecha_emision'] = base_date.strftime('%Y-%m-%d')
df_recetas.to_csv(f"{OUTPUT_DIR}/recetas_medicas.csv", index=False)

df_detalles = pd.DataFrame({'id_receta': range(1, len(df_recetas) + 1)})
df_detalles['id_medicamento'] = 1 
df_detalles['dosis'] = '500 mg'
df_detalles['frecuencia'] = 'Cada 8 horas'
df_detalles['duracion_dias'] = 5
df_detalles.to_csv(f"{OUTPUT_DIR}/detalles_recetas.csv", index=False)

print(f"\n[!] NORMALIZACIÓN COMPLETADA. 11 archivos guardados en '{OUTPUT_DIR}/'")