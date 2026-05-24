
---

## ⚙️ Requisitos previos

- **Python 3.9+** y pip
- **Docker** y **Docker Compose** (para la ejecución contenerizada)
- Acceso a Internet para descargar los datasets desde Kaggle
- (Opcional) Git

---

## 🔄 Proceso de normalización (resumen)

### 1FN – Primera Forma Normal
- **Violaciones típicas**: columnas con listas separadas por comas (ej. `directores`, `países`, `géneros` en Netflix).
- **Solución**: dividir esos valores en filas separadas, creando tablas adicionales (ej. `show_director`, `show_country`, `show_genre`).

### 2FN – Segunda Forma Normal
- **Condición**: estar en 1FN y eliminar dependencias parciales (atributos que dependen solo de parte de una clave compuesta).
- **Ejemplo**: en E‑commerce, una clave `(order_id, product_id)` → atributos como `customer_name` dependen solo de `order_id`. Se extrae una tabla `Orders`.

### 3FN – Tercera Forma Normal
- **Condición**: estar en 2FN y eliminar dependencias transitivas (atributo no clave que depende de otro no clave).
- **Ejemplo**: en Hospital, `doctor_name` → `doctor_department`. Se crea una tabla `Doctors` independiente de `Patient_Visits`.

Para cada dataset se documentan:
- Tabla comparativa (número de tablas, columnas, redundancia estimada, anomalías eliminadas).
- Diagramas Entidad‑Relación Extendido (EER) y modelo relacional final.

---

## 🤖 Automatización con scripts

Los scripts en Python (`scripts/normalize_*.py`) realizan:

1. **Carga** del CSV original con pandas.
2. **Detección automática** de columnas multivaluadas (mediante expresiones regulares y umbral de comas).
3. **Normalización**:
   - 1FN: explode de listas y creación de tablas auxiliares.
   - 2FN y 3FN: análisis de dependencias (definidas en el código mediante reglas pre‑estudiadas para cada dataset).
4. **Generación de resultados**:
   - Archivos CSV separados por tabla (en `data/normalized/`).
   - Scripts DDL y DML (en `sql/ddl/` y `sql/dml/`).
   - Opción de cargar directamente a una base de datos SQLite/PostgreSQL.

### Ejecución sin Docker

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar para un dataset (ej. Netflix)
python scripts/normalize_netflix.py

# O ejecutar los tres
for script in scripts/normalize_*.py; do python $script; done
