# Análisis Original de los Datasets
**Práctica 6 – Normalización de Bases de Datos**  
Instituto Politécnico Nacional · Escuela Superior de Cómputo  
Ingeniería en Sistemas Computacionales 2020 · Bases de Datos

---

## Dataset 1: Netflix Movies and TV Shows

### 1.1 Estructura original

| Columna | Tipo de dato | Descripción |
|---|---|---|
| show_id | VARCHAR | Identificador único del título (`s1`, `s2`, …) |
| type | VARCHAR | `Movie` o `TV Show` |
| title | VARCHAR | Título del contenido |
| director | TEXT | Lista separada por comas de directores |
| cast | TEXT | Lista separada por comas de actores |
| country | TEXT | Lista separada por comas de países de producción |
| date_added | VARCHAR | Fecha de alta en la plataforma (texto libre) |
| release_year | INTEGER | Año de estreno |
| rating | VARCHAR | Clasificación de audiencia (PG-13, TV-MA, …) |
| duration | VARCHAR | Duración compuesta: `90 min` o `2 Seasons` |
| listed_in | TEXT | Lista separada por comas de géneros |
| description | TEXT | Sinopsis del título |

- **Total de registros:** ~8,800  
- **Total de columnas:** 12

#### 5 registros representativos

| show_id | type | title | director | cast | country | release_year | rating | duration | listed_in |
|---|---|---|---|---|---|---|---|---|---|
| s1 | TV Show | Dick Johnson Is Dead | Kirsten Johnson | — | United States | 2020 | PG-13 | 1 Season | Documentaries |
| s2 | TV Show | Blood & Water | — | Ama Qamata, Khosi Ngema | South Africa | 2021 | TV-MA | 2 Seasons | International TV Shows, TV Dramas |
| s3 | TV Show | Ganglands | Julien Leclercq | Sami Bouajila, Tracy Gotoas | France, Belgium | 2021 | TV-MA | 1 Season | Crime TV Shows, International TV Shows |
| s4 | Movie | Jailbirds New Orleans | — | — | — | 2021 | TV-MA | 98 min | Docuseries, Reality TV |
| s5 | TV Show | Kota Factory | — | Mayur More, Jitendra Kumar | India | 2021 | TV-MA | 2 Seasons | International TV Shows, Romantic TV Shows |

### 1.2 Problemas de normalización identificados

#### Violaciones de 1FN
- `director`: múltiples valores separados por coma (ej. `"Anthony Russo, Joe Russo"`).
- `cast`: lista de actores en un solo campo.
- `country`: varios países en un mismo campo.
- `listed_in`: múltiples géneros concatenados.

#### Violaciones de 2FN
No aplica directamente (clave primaria simple `show_id`), pero el campo `duration` es compuesto: almacena valor numérico y unidad juntos.

#### Violaciones de 3FN
- `rating` → `descripción del rating`: la descripción de la clasificación (`PG-13 = "Parents Strongly Cautioned"`) depende transitivamente de `rating`, no de `show_id`.
- `type` → `descripción del tipo`: la descripción de Movie/TV Show es un atributo del tipo, no del título.

#### Redundancias
- El nombre de un director o actor se repite íntegramente en cada uno de los títulos donde aparece.
- El nombre de un país se repite en cada título de producción de ese país.
- Los géneros se repiten literalmente en miles de filas.

#### Anomalías potenciales
| Anomalía | Ejemplo |
|---|---|
| Inserción | No es posible registrar a un director sin que tenga al menos un título. |
| Actualización | Renombrar un género requiere modificar cientos de filas; riesgo de inconsistencia. |
| Eliminación | Eliminar el último título de un actor borra su información de la base de datos. |

### 1.3 Dependencias funcionales

```
show_id → type, title, date_added, release_year, rating, duration, description
show_id →→ director      (multivaluada)
show_id →→ cast          (multivaluada)
show_id →→ country       (multivaluada)
show_id →→ listed_in     (multivaluada)
rating  → descripcion_rating     (transitiva)
type    → descripcion_tipo       (transitiva)
duration_texto → duracion_valor, duracion_unidad  (atributo compuesto)
```

---

## Dataset 2: E-commerce Sales Data

### 2.1 Estructura original

| Columna | Tipo de dato | Descripción |
|---|---|---|
| InvoiceNo | VARCHAR | Número de factura (6 dígitos; prefijo `C` = cancelada) |
| StockCode | VARCHAR | Código de producto |
| Description | VARCHAR | Nombre del producto |
| Quantity | INTEGER | Cantidad facturada |
| InvoiceDate | DATETIME | Fecha y hora de la factura |
| UnitPrice | DECIMAL | Precio unitario en libras esterlinas |
| CustomerID | FLOAT | Identificador del cliente (puede ser NaN) |
| Country | VARCHAR | País del cliente |

- **Total de registros:** ~541,000  
- **Total de columnas:** 8

#### 5 registros representativos

| InvoiceNo | StockCode | Description | Quantity | InvoiceDate | UnitPrice | CustomerID | Country |
|---|---|---|---|---|---|---|---|
| 536365 | 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 6 | 2010-12-01 08:26 | 2.55 | 17850 | United Kingdom |
| 536365 | 71053 | WHITE METAL LANTERN | 6 | 2010-12-01 08:26 | 3.39 | 17850 | United Kingdom |
| 536366 | 22633 | HAND WARMER UNION JACK | 6 | 2010-12-01 08:28 | 1.85 | 17850 | United Kingdom |
| 536367 | 84879 | ASSORTED COLOUR BIRD ORNAMENT | 32 | 2010-12-01 08:34 | 1.69 | 13047 | United Kingdom |
| 536368 | 22960 | JAM MAKING SET WITH JARS | 6 | 2010-12-01 08:34 | 4.25 | 13047 | United Kingdom |

### 2.2 Problemas de normalización identificados

#### Violaciones de 1FN
Los datos son atómicos por columna, pero la tabla mezcla información de múltiples entidades en una sola fila.

#### Violaciones de 2FN
La clave compuesta real es `(InvoiceNo, StockCode)`:
- `Description` depende solo de `StockCode` (no de `InvoiceNo`). → dependencia parcial.
- `CustomerID`, `InvoiceDate`, `Country` dependen solo de `InvoiceNo` (no de `StockCode`). → dependencia parcial.

#### Violaciones de 3FN
- `CustomerID` → `Country`: el país del cliente es un atributo del cliente, no de la factura. Dependencia transitiva: `InvoiceNo → CustomerID → Country`.

#### Redundancias
- El nombre del producto (`Description`) se repite en todas las líneas de la factura donde aparece el mismo `StockCode`.
- El país del cliente se repite en cada línea de cada factura de ese cliente.

#### Anomalías potenciales
| Anomalía | Ejemplo |
|---|---|
| Inserción | No se puede registrar un producto sin haber generado al menos una factura. |
| Actualización | Cambiar la descripción de un producto requiere actualizar miles de filas. |
| Eliminación | Eliminar todas las facturas de un cliente elimina también su información de país. |

### 2.3 Dependencias funcionales

```
(InvoiceNo, StockCode) → Quantity, UnitPrice
StockCode  → Description                        (dependencia parcial)
InvoiceNo  → CustomerID, InvoiceDate, Country   (dependencia parcial)
CustomerID → Country                            (dependencia transitiva)
```

---

## Dataset 3: Hospital Patient Records

### 3.1 Estructura original (selección de columnas relevantes)

| Columna | Tipo de dato | Descripción |
|---|---|---|
| encounter_id | INTEGER | Identificador único del encuentro clínico |
| patient_id | INTEGER | Identificador del paciente |
| hospital_id | INTEGER | Identificador del hospital / médico tratante |
| age | INTEGER | Edad del paciente |
| gender | VARCHAR | Género del paciente (M / F) |
| icu_id | INTEGER | Identificador de la UCI / habitación |
| icu_admit_source | VARCHAR | Fuente de admisión (= aseguradora/origen) |
| apache_3j_bodysystem | VARCHAR | Sistema corporal APACHE III (= especialidad) |
| pre_icu_los_days | FLOAT | Días previos a UCI |

- **Total de registros:** variable (~130,000 en el dataset completo; se usaron hasta 5,000 en pruebas)  
- **Total de columnas relevantes:** 9+ de ~186 totales

#### 5 registros representativos

| encounter_id | patient_id | hospital_id | age | gender | icu_id | icu_admit_source | apache_3j_bodysystem |
|---|---|---|---|---|---|---|---|
| 100001 | 10001 | 458 | 68 | M | 92 | Floor | Cardiovascular |
| 100002 | 10002 | 253 | 54 | F | 118 | Accident & Emergency | Neurological |
| 100003 | 10003 | 244 | 77 | M | 88 | Floor | Metabolic |
| 100004 | 10004 | 458 | 45 | F | 92 | Accident & Emergency | Cardiovascular |
| 100005 | 10005 | 244 | 30 | M | 88 | Floor | Neurological |

### 3.2 Problemas de normalización identificados

#### Violaciones de 1FN
Los campos individuales son atómicos, pero la tabla combina atributos de múltiples entidades del dominio hospitalario en una sola estructura plana.

#### Violaciones de 2FN
La clave primaria es `encounter_id`, pero varios atributos dependen de otras entidades:
- `age`, `gender` → dependen de `patient_id`, no del encuentro.
- `apache_3j_bodysystem` → depende de `hospital_id` (especialidad del médico).
- Características de la UCI → dependen de `icu_id`.

#### Violaciones de 3FN
- `icu_admit_source` actúa como código de aseguradora; sus atributos (teléfono, etc.) dependerían transitivamente de `encounter_id` a través del paciente.
- `apache_3j_bodysystem` (especialidad) es un atributo del médico/hospital, no del encuentro.

#### Redundancias
- Los datos demográficos del paciente (edad, género) se repiten en cada encounter del mismo paciente.
- La especialidad del médico se repite en cada encounter asociado a ese hospital.
- El nombre de la UCI/habitación se repite en todos los encuentros de esa UCI.

#### Anomalías potenciales
| Anomalía | Ejemplo |
|---|---|
| Inserción | No se puede registrar un médico o paciente sin un encounter activo. |
| Actualización | Cambiar la especialidad de un hospital requiere actualizar todos sus encounters. |
| Eliminación | Eliminar los encounters de un paciente elimina su información demográfica. |

### 3.3 Dependencias funcionales

```
encounter_id → patient_id, hospital_id, icu_id, icu_admit_source, pre_icu_los_days, apache_3j_bodysystem
patient_id   → age, gender, icu_admit_source   (transitiva a través del encounter)
hospital_id  → apache_3j_bodysystem            (transitiva: especialidad del médico)
icu_id       → número de habitación, tipo, estado
```

---

## Resumen comparativo de problemas detectados

| Dataset | Violaciones 1FN | Violaciones 2FN | Violaciones 3FN | Redundancia estimada |
|---|---|---|---|---|
| Netflix | Alta (4 columnas multivalor) | Media (campo compuesto `duration`) | Alta (rating, tipo) | ~60–70 % |
| E-commerce | Baja (campos atómicos) | Alta (dependencias parciales claras) | Alta (país transitivo) | ~40–50 % |
| Hospital | Media (tabla monolítica) | Alta (atributos de otras entidades) | Alta (especialidad, aseguradora) | ~50–60 % |
