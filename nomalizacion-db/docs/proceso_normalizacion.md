# Proceso de Normalización de Bases de Datos
**Práctica 6 – Normalización de Bases de Datos**  
Instituto Politécnico Nacional · Escuela Superior de Cómputo  
Ingeniería en Sistemas Computacionales 2020 · Bases de Datos

---

## Dataset 1: Netflix Movies and TV Shows

### 1FN — Primera Forma Normal

**Punto de partida:** tabla `netflix_titles` con 12 columnas, ~8,800 filas.

**Violaciones identificadas:**
- `director`, `cast`, `country`, `listed_in`: múltiples valores separados por coma en un campo.
- `duration`: valor compuesto (`"90 min"`, `"2 Seasons"`).

**Transformaciones aplicadas:**

1. Se separó `duration` en dos columnas atómicas: `duracion_valor (SMALLINT)` y `duracion_unidad (VARCHAR)`.
2. Las columnas multivaluadas no se expandieron directamente en la misma tabla (lo que generaría grupos repetitivos), sino que se crearon tablas independientes para cada entidad implícita: personas (directores/actores), países y géneros.
3. Se definió `show_id` como clave primaria de la tabla `titulos`.

**Estructura resultante en 1FN:**

```
titulos(show_id PK, id_tipo, id_clasificacion, titulo, fecha_agregado,
        anio_estreno, duracion_valor, duracion_unidad, descripcion)
```
Tablas auxiliares de apoyo (listas aún sin relaciones formalizadas):
- lista temporal de directores por show_id
- lista temporal de actores por show_id
- lista temporal de países por show_id
- lista temporal de géneros por show_id

---

### 2FN — Segunda Forma Normal

**Punto de partida:** estructura en 1FN.

La clave primaria de `titulos` es simple (`show_id`), por lo que las dependencias parciales provienen de las listas temporales donde la clave compuesta es `(show_id, nombre_entidad)`.

**Dependencias parciales identificadas:**
- `nombre_director` depende solo del director, no del título.
- `nombre_actor` depende solo del actor, no del título.
- `nombre_pais` depende solo del país.
- `nombre_genero` depende solo del género.
- Los atributos de clasificación (`descripcion`) dependen de `rating`, no de `show_id`.
- Los atributos del tipo (`descripcion_tipo`) dependen de `type`, no de `show_id`.

**Transformaciones aplicadas:**

Se separaron las entidades independientes en catálogos propios:

```
cat_tipos_contenido(id_tipo PK, nombre_tipo, descripcion)
cat_clasificaciones(id_clasificacion PK, codigo, descripcion)
cat_paises(id_pais PK, nombre)
cat_generos(id_genero PK, nombre)
personas(id_persona PK, nombre_completo)
```

La tabla `titulos` mantiene FK a `cat_tipos_contenido` e `id_clasificacion`.

---

### 3FN — Tercera Forma Normal

**Punto de partida:** estructura en 2FN.

**Dependencias transitivas identificadas:**
- `show_id → rating → descripcion_rating`: la descripción del rating depende de `rating`, no de `show_id`. → resuelta en `cat_clasificaciones`.
- `show_id → type → descripcion_tipo`: resuelta en `cat_tipos_contenido`.
- Las relaciones N:M pendientes (actor–título, director–título, etc.) se materializaron como tablas de asociación.

**Estructura final en 3FN:**

```
cat_tipos_contenido(id_tipo PK, nombre_tipo, descripcion)
cat_clasificaciones(id_clasificacion PK, codigo, descripcion)
cat_paises(id_pais PK, nombre)
cat_generos(id_genero PK, nombre)

personas(id_persona PK, nombre_completo)

titulos(id_titulo PK, show_id UNIQUE, id_tipo FK, id_clasificacion FK,
        titulo, fecha_agregado, anio_estreno,
        duracion_valor, duracion_unidad, descripcion, created_at)

titulo_directores(id_titulo FK, id_persona FK)       PK(id_titulo, id_persona)
titulo_actores(id_titulo FK, id_persona FK,
               orden_credito)                        PK(id_titulo, id_persona)
titulo_paises(id_titulo FK, id_pais FK, es_primario) PK(id_titulo, id_pais)
titulo_generos(id_titulo FK, id_genero FK)           PK(id_titulo, id_genero)
```

Vista de conveniencia `v_titulos_planos` reconstruye el formato plano original para consultas BI.

### Tabla comparativa Dataset 1

| Aspecto | Original | 1FN | 2FN | 3FN |
|---|---|---|---|---|
| Número de tablas | 1 | 1 + listas temp. | 5 | 10 |
| Total de columnas | 12 | ~10 | ~25 | ~35 |
| Redundancia estimada | ~65 % | ~50 % | ~25 % | <5 % |
| Anomalías de inserción | Sí | Parcial | Parcial | No |
| Anomalías de actualización | Sí | Sí | Parcial | No |
| Anomalías de eliminación | Sí | Sí | Parcial | No |
| Integridad referencial | No | No | Parcial | Completa |

---

## Dataset 2: E-commerce Sales Data

### 1FN — Primera Forma Normal

**Punto de partida:** tabla `ecommerce_raw` con 8 columnas, ~541,000 filas.

**Verificación de atomicidad:** cada celda ya contiene un único valor atómico. No hay campos multivaluados en el sentido estricto; la violación principal es que la tabla agrupa información de múltiples entidades.

**Clave primaria compuesta definida:** `(invoice_no, stock_code)`.

**Estructura en 1FN:**
```
ecommerce_raw(invoice_no, stock_code, description, quantity,
              invoice_date, unit_price, customer_id, country)
```

---

### 2FN — Segunda Forma Normal

**Punto de partida:** estructura en 1FN, clave compuesta `(invoice_no, stock_code)`.

**Dependencias parciales identificadas:**
- `description` → depende solo de `stock_code`.
- `customer_id`, `invoice_date`, `country` → dependen solo de `invoice_no`.

**Transformaciones aplicadas:**

```
products(stock_code PK, description)

invoices_raw(invoice_no PK, customer_id, invoice_date, country)

invoice_items(item_id PK, invoice_no FK, stock_code FK,
              quantity, unit_price)
```

---

### 3FN — Tercera Forma Normal

**Punto de partida:** estructura en 2FN.

**Dependencia transitiva identificada:**
- `invoice_no → customer_id → country`: el país es un atributo del cliente, no de la factura.

**Transformaciones aplicadas:**

```
countries(country_id PK, country_name)

customers(customer_id PK, country_id FK)

invoices(invoice_no PK, customer_id FK, invoice_date)

products(stock_code PK, description)

invoice_items(item_id PK, invoice_no FK, stock_code FK,
              quantity, unit_price)
```

### Tabla comparativa Dataset 2

| Aspecto | Original | 1FN | 2FN | 3FN |
|---|---|---|---|---|
| Número de tablas | 1 | 1 | 3 | 5 |
| Total de columnas | 8 | 8 | 12 | 15 |
| Redundancia estimada | ~45 % | ~45 % | ~20 % | <5 % |
| Anomalías de inserción | Sí | Sí | Parcial | No |
| Anomalías de actualización | Sí | Sí | Parcial | No |
| Anomalías de eliminación | Sí | Sí | Parcial | No |
| Integridad referencial | No | No | Parcial | Completa |

---

## Dataset 3: Hospital Patient Records

### 1FN — Primera Forma Normal

**Punto de partida:** tabla `dataset` con ~186 columnas, hasta ~130,000 filas (se limitó a 5,000 en pruebas).

**Verificación de atomicidad:** los campos relevantes son atómicos. Sin embargo, la tabla es monolítica y mezcla todas las entidades del dominio hospitalario.

**Clave primaria definida:** `encounter_id`.

**Estructura base en 1FN:** tabla `dataset` tal cual, con `encounter_id` como PK.

---

### 2FN — Segunda Forma Normal

**Clave primaria simple:** `encounter_id`, por lo que las dependencias parciales se expresan como atributos que dependen de otras entidades identificadas dentro de la tabla.

**Dependencias de otras claves identificadas:**
- `age`, `gender`, `icu_admit_source` → dependen de `patient_id`.
- `apache_3j_bodysystem` → depende de `hospital_id` (especialidad del médico).
- Tipo y número de habitación → dependen de `icu_id`.

**Transformaciones aplicadas:**

Se extrajeron catálogos independientes de los valores repetitivos:

```
cat_especialidades(id_especialidad PK, nombre_especialidad)
cat_aseguradoras(id_aseguradora PK, nombre_aseguradora, telefono_contacto)
cat_habitaciones(id_habitacion PK, numero_habitacion, tipo_habitacion, estado_habitacion)
cat_medicamentos(id_medicamento PK, nombre_comercial, componente_activo, presentacion)
```

---

### 3FN — Tercera Forma Normal

**Punto de partida:** estructura en 2FN.

**Dependencias transitivas identificadas:**
- `encounter_id → patient_id → age, gender, id_aseguradora`: los datos demográficos del paciente dependen del paciente, no del encuentro.
- `encounter_id → hospital_id → id_especialidad`: la especialidad médica depende del médico.
- `encounter_id → icu_id → numero_habitacion, tipo_habitacion`: atributos de la UCI.

**Transformaciones aplicadas:**

```
medicos(id_medico PK, nombre, apellido, cedula_profesional,
        id_especialidad FK, telefono, email)

pacientes(id_paciente PK, nombre, apellido, fecha_nacimiento,
          genero, telefono, email, id_aseguradora FK, nss_seguro)

citas_medicas(id_cita PK, id_paciente FK, id_medico FK,
              fecha_hora, motivo_consulta, estado_cita)

ingresos_hospitalarios(id_ingreso PK, id_paciente FK, id_habitacion FK,
                       fecha_ingreso, fecha_alta, motivo_ingreso)

historiales_clinicos(id_historial PK, id_paciente FK, id_medico FK,
                     fecha_registro, sintomas, diagnostico)

recetas_medicas(id_receta PK, id_historial FK, fecha_emision)

detalles_recetas(id_detalle PK, id_receta FK, id_medicamento FK,
                 dosis, frecuencia, duracion_dias)
```

### Tabla comparativa Dataset 3

| Aspecto | Original | 1FN | 2FN | 3FN |
|---|---|---|---|---|
| Número de tablas | 1 | 1 | 5 | 11 |
| Total de columnas | ~186 | ~186 | ~50 | ~60 |
| Redundancia estimada | ~55 % | ~55 % | ~20 % | <5 % |
| Anomalías de inserción | Sí | Sí | Parcial | No |
| Anomalías de actualización | Sí | Sí | Parcial | No |
| Anomalías de eliminación | Sí | Sí | Parcial | No |
| Integridad referencial | No | No | Parcial | Completa |

---

## Conclusiones del proceso de normalización

1. **1FN** resuelve la atomicidad de los valores y establece claves primarias claras. El impacto más visible ocurre en el Dataset 1 (Netflix), donde cuatro columnas multivaluadas se descomponen en entidades independientes.

2. **2FN** elimina la redundancia por dependencias parciales. El impacto más claro se da en el Dataset 2 (E-commerce), donde la descripción del producto se almacenaba repetida en cada línea de factura.

3. **3FN** elimina las dependencias transitivas, produciendo un modelo donde cada atributo no clave depende directamente de la PK. En los tres datasets esto se traduce en la extracción de catálogos controlados (tipos, clasificaciones, países, especialidades) que garantizan consistencia mediante claves foráneas.

4. El número de tablas crece de 1 a 10–11 por dataset, pero la redundancia se reduce a menos del 5 % y desaparecen las anomalías de inserción, actualización y eliminación.
