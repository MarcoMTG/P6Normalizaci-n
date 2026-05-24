# Práctica 6: Normalización de Bases de Datos
## Dataset 2: E-commerce Sales Data

**Instituto Politécnico Nacional — ESCOM**  
**Materia:** Bases de Datos | **Plan:** Ingeniería en Sistemas Computacionales 2020  
**Entrega:** 25 de mayo de 2026

---

## Ejercicio 1 — Análisis Inicial del Dataset

### 1.1 Estructura Original

| Atributo | Valor |
|---|---|
| Fuente | Kaggle — E-Commerce Data (Carrie1) |
| Archivo | `data.csv` |
| Registros totales | 541,909 filas |
| Columnas | 8 |
| Formato | CSV (encoding Latin-1) |

#### Columnas y tipos de datos

| Columna | Tipo original | Descripción |
|---|---|---|
| `InvoiceNo` | String/Integer | Número de factura |
| `StockCode` | String | Código de producto |
| `Description` | String | Nombre del producto |
| `Quantity` | Integer | Unidades vendidas |
| `InvoiceDate` | String (fecha) | Fecha y hora de la venta |
| `UnitPrice` | Float | Precio unitario en libras esterlinas |
| `CustomerID` | Float (nullable) | Identificador del cliente |
| `Country` | String | País del cliente |

#### 5 registros representativos

| InvoiceNo | StockCode | Description | Quantity | InvoiceDate | UnitPrice | CustomerID | Country |
|---|---|---|---|---|---|---|---|
| 536365 | 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 6 | 12/1/2010 8:26 | 2.55 | 17850.0 | United Kingdom |
| 536365 | 71053 | WHITE METAL LANTERN | 6 | 12/1/2010 8:26 | 3.39 | 17850.0 | United Kingdom |
| 536366 | 22633 | HAND WARMER UNION JACK | 6 | 12/1/2010 8:28 | 1.85 | 17850.0 | United Kingdom |
| 536367 | 84879 | ASSORTED COLOUR BIRD ORNAMENT | 32 | 12/1/2010 8:34 | 1.69 | 13047.0 | United Kingdom |
| 536370 | 22728 | ALARM CLOCK BAKELIKE GREEN | 24 | 12/1/2010 8:45 | 3.75 | 12583.0 | France |

---

### 1.2 Problemas de Normalización Identificados

#### Violaciones de 1FN
- **No hay columnas multivaluadas** en sentido estricto (sin listas separadas por comas).  
- Sin embargo, hay **1,454 valores NULL en `Description`** (celdas no atómicas por ausencia).  
- Cada fila mezcla datos de entidades distintas: cliente, producto, factura y línea de detalle.

#### Dependencias parciales — Violación de 2FN

La clave primaria natural de la tabla es compuesta: **(InvoiceNo, StockCode)**.  
Se detectaron los siguientes atributos que dependen **solo de una parte** de la clave:

| Atributo | Depende de | Problema |
|---|---|---|
| `Description` | Solo de `StockCode` | Dependencia parcial |
| `UnitPrice` | Solo de `StockCode` (precio del producto) | Dependencia parcial |
| `CustomerID` | Solo de `InvoiceNo` | Dependencia parcial |
| `InvoiceDate` | Solo de `InvoiceNo` | Dependencia parcial |
| `Country` | Solo de `InvoiceNo` | Dependencia parcial |

#### Dependencias transitivas — Violación de 3FN

Una vez resueltas las dependencias parciales, en la tabla `invoices` quedaría:

```
InvoiceNo → CustomerID → Country
```

Es decir, `Country` depende transitivamente de `InvoiceNo` **a través de** `CustomerID`.  
Un cliente siempre pertenece al mismo país (en general), por lo que `Country` debe vivir en la tabla de clientes o en una tabla de países.

#### Redundancia de datos

- La descripción del mismo producto se repite en **cada línea** donde aparece ese producto.  
- El país del cliente se repite en **cada factura** del mismo cliente.  
- Con 541,909 filas y solo 4,070 productos únicos, hay una redundancia masiva en `Description`.

#### Anomalías identificadas

| Tipo | Descripción |
|---|---|
| **Inserción** | No se puede insertar un producto sin que exista una factura; ni un cliente sin transacción. |
| **Actualización** | Cambiar el nombre de un producto requiere actualizar miles de filas (ej: `Description`). |
| **Eliminación** | Borrar la única factura de un cliente elimina toda la información del cliente. |

---

### 1.3 Diagrama de Dependencias Funcionales (estado original)

```
(InvoiceNo, StockCode)  ──────────────────────────────► Quantity
       │                                                 UnitPrice (¡también depende solo de StockCode!)
       │
       ├── InvoiceNo ──► CustomerID
       │                    │
       │                    └──► Country          ← dependencia transitiva
       │              ──► InvoiceDate
       │
       └── StockCode ──► Description              ← dependencia parcial
                    ──► UnitPrice                 ← dependencia parcial

Leyenda:
  ──►  Dependencia funcional
  (X)  Dependencia problemática (parcial o transitiva)
```

---

## Ejercicio 2 — Proceso de Normalización Manual

### 2.1 Primera Forma Normal (1FN)

**Punto de partida:** tabla única `data` con 541,909 filas y 8 columnas.

**Requisitos de 1FN:**
1. Cada celda contiene un único valor atómico ✅ (el CSV ya tiene valores simples)
2. Cada registro es único — se requiere definir clave primaria
3. No hay grupos repetitivos en una misma fila ✅

**Transformaciones realizadas:**

1. Se define la **clave primaria compuesta**: `(InvoiceNo, StockCode)`.
2. Se eliminan filas con `CustomerID = NULL` (135,080 registros sin identificación de cliente) para garantizar integridad referencial.
3. Se convierte `CustomerID` de float a entero.
4. Se convierte `InvoiceDate` al formato estándar `DATETIME`.

**Estructura resultante en 1FN:**

| invoice_no | stock_code | description | quantity | invoice_date | unit_price | customer_id | country |
|---|---|---|---|---|---|---|---|
| 536365 | 85123A | WHITE HANGING… | 6 | 2010-12-01 08:26 | 2.55 | 17850 | United Kingdom |

**Estadísticas tras 1FN:**
- Filas válidas: **406,829**
- Columnas: **8** (sin cambios estructurales)
- Tablas: **1**

---

### 2.2 Segunda Forma Normal (2FN)

**Punto de partida:** tabla única en 1FN con clave compuesta `(invoice_no, stock_code)`.

**Dependencias parciales identificadas y eliminadas:**

#### Nueva tabla: `products`
Contiene los atributos que dependen **solo de** `stock_code`:

```
stock_code → description
```

| stock_code | description |
|---|---|
| 85123A | WHITE HANGING HEART T-LIGHT HOLDER |
| 71053 | WHITE METAL LANTERN |
| 84406B | CREAM CUPID HEARTS COAT HANGER |

- **Filas:** 3,684 (productos únicos)

#### Nueva tabla: `invoices` (parcial)
Contiene los atributos que dependen **solo de** `invoice_no`:

```
invoice_no → customer_id, invoice_date, country
```

| invoice_no | customer_id | invoice_date | country |
|---|---|---|---|
| 536365 | 17850 | 2010-12-01 08:26 | United Kingdom |
| 536366 | 17850 | 2010-12-01 08:28 | United Kingdom |

- **Filas:** 22,190 (facturas únicas)

#### Nueva tabla: `invoice_items`
Conserva solo lo que depende de **toda** la clave compuesta:

```
(invoice_no, stock_code) → quantity, unit_price
```

| item_id | invoice_no | stock_code | quantity | unit_price |
|---|---|---|---|---|
| 1 | 536365 | 85123A | 6 | 2.55 |
| 2 | 536365 | 71053 | 6 | 3.39 |

- **Filas:** 406,829

**Diagrama entidad-relación en 2FN:**
```
invoices ──┐
           ├──► invoice_items ◄──┤
products ──┘                     └── (stock_code FK)
```

---

### 2.3 Tercera Forma Normal (3FN)

**Punto de partida:** tablas en 2FN. En la tabla `invoices` existe la dependencia transitiva:

```
invoice_no → customer_id → country
```

`Country` no describe a la factura, describe al **cliente**.  
Y si distintos clientes del mismo país cambian de país, habría inconsistencias.

**Transformaciones realizadas:**

#### Nueva tabla: `countries`
Se extrae el catálogo de países independiente:

```
country_id → country_name
```

| country_id | country_name |
|---|---|
| 1 | Australia |
| 2 | Austria |
| 3 | Bahrain |
| … | … |
| 37 | Unspecified |

- **Filas:** 37

#### Tabla modificada: `customers`
El cliente referencia al país por llave foránea, eliminando la redundancia:

```
customer_id → country_id
```

| customer_id | country_id |
|---|---|
| 17850 | 36 |
| 13047 | 36 |
| 12583 | 11 |

- **Filas:** 4,372

#### Tabla final: `invoices`
Ya sin `country` (que ahora vive en `customers`):

```
invoice_no → customer_id, invoice_date
```

| invoice_no | customer_id | invoice_date |
|---|---|---|
| 536365 | 17850 | 2010-12-01 08:26 |

- **Filas:** 22,190

---

### 2.4 Modelo Relacional Completo (3FN)

```
countries
  PK: country_id (INTEGER)
  ├── country_name (VARCHAR 100) NOT NULL UNIQUE

customers
  PK: customer_id (INTEGER)
  FK: country_id → countries.country_id
  └── country_id (INTEGER) NOT NULL

products
  PK: stock_code (VARCHAR 20)
  └── description (VARCHAR 255)

invoices
  PK: invoice_no (VARCHAR 20)
  FK: customer_id → customers.customer_id
  ├── customer_id (INTEGER) NOT NULL
  └── invoice_date (DATETIME) NOT NULL

invoice_items
  PK: item_id (INTEGER AUTOINCREMENT)
  FK: invoice_no → invoices.invoice_no
  FK: stock_code → products.stock_code
  ├── invoice_no (VARCHAR 20) NOT NULL
  ├── stock_code (VARCHAR 20) NOT NULL
  ├── quantity   (INTEGER)    NOT NULL
  └── unit_price (DECIMAL 10,2) NOT NULL
```

### 2.5 Tabla Comparativa

| Aspecto | Original | 1FN | 2FN | 3FN |
|---|---|---|---|---|
| Número de tablas | 1 | 1 | 3 | 5 |
| Total de columnas | 8 | 8 | 14 | 13 |
| Filas totales | 541,909 | 406,829 | 432,703 | 437,112 |
| Redundancia estimada | Alta (~60%) | Alta (~60%) | Media (~30%) | Baja (<5%) |
| Anomalías de inserción | Sí | Sí | Parcialmente | No |
| Anomalías de actualización | Sí | Sí | Parcialmente | No |
| Anomalías de eliminación | Sí | Sí | Parcialmente | No |
| Integridad referencial | No | No | Parcial | Sí (FKs explícitas) |

---

## Ejercicio 3 — Automatización

Ver carpeta `scripts/` del proyecto:

- `scripts/utils.py` — funciones auxiliares (carga, limpieza, exportación, reporte)
- `scripts/normalize_dataset2.py` — script principal de normalización automatizada

**Cómo ejecutar:**

```bash
pip install pandas
python scripts/normalize_dataset2.py
```

**Salidas generadas automáticamente:**

| Archivo | Ubicación | Descripción |
|---|---|---|
| `countries.csv` | `data/normalized/ecommerce/` | Catálogo de países |
| `customers.csv` | `data/normalized/ecommerce/` | Clientes normalizados |
| `products.csv` | `data/normalized/ecommerce/` | Catálogo de productos |
| `invoices.csv` | `data/normalized/ecommerce/` | Facturas |
| `invoice_items.csv` | `data/normalized/ecommerce/` | Líneas de detalle |
| `ecommerce_3fn.db` | `data/normalized/ecommerce/` | Base de datos SQLite |
| `dataset2_schema.sql` | `sql/ddl/` | DDL (CREATE TABLE) |
| `dataset2_data.sql` | `sql/dml/` | DML muestra (INSERT) |

**Resultado de ejecución:**

```
[1/5] Cargando dataset original...
     Filas totales  : 541,909
     Filas tras limpiar NaN en CustomerID: 406,829

[2/5] 1FN — verificando atomicidad...
[3/5] 2FN — eliminando dependencias parciales...
     products       : 3,684 filas
     invoices (raw) : 22,190 filas
     invoice_items  : 406,829 filas

[4/5] 3FN — eliminando dependencias transitivas...
     countries      : 37 filas
     customers      : 4,372 filas
     invoices       : 22,190 filas

[5/5] Exportando resultados...

===== REPORTE DE NORMALIZACIÓN =====
Celdas originales :  4,335,272
Celdas normalizadas:  2,116,901
Reducción estimada:      51.2%
=====================================
✅ Normalización completada exitosamente.
```

---

## Ejercicio 5 — Diagrama EER

```
┌──────────────┐         ┌──────────────────┐        ┌───────────────┐
│  countries   │  1    N │    customers     │  1   N │   invoices    │
│──────────────│─────────│──────────────────│────────│───────────────│
│ PK country_id│         │ PK customer_id   │        │ PK invoice_no │
│ country_name │         │ FK country_id    │        │ FK customer_id│
└──────────────┘         └──────────────────┘        │ invoice_date  │
                                                      └───────┬───────┘
                                                              │ 1
                                                              │
                                                              │ N
                                                    ┌─────────┴──────────┐
                                                    │   invoice_items    │
                                                    │────────────────────│
                                                    │ PK item_id         │
                                                    │ FK invoice_no      │
                                                    │ FK stock_code      │
                                                    │ quantity           │
                                                    │ unit_price         │
                                                    └─────────┬──────────┘
                                                              │ N
                                                              │
                                                              │ 1
                                                    ┌─────────┴──────────┐
                                                    │      products      │
                                                    │────────────────────│
                                                    │ PK stock_code      │
                                                    │ description        │
                                                    └────────────────────┘

Cardinalidades:
  countries  1 ──── N  customers     (un país tiene muchos clientes)
  customers  1 ──── N  invoices      (un cliente tiene muchas facturas)
  invoices   1 ──── N  invoice_items (una factura tiene muchas líneas)
  products   1 ──── N  invoice_items (un producto aparece en muchas líneas)
```

---

*Práctica 6 — Normalización de Bases de Datos*  
*ESCOM — IPN — Bases de Datos 2020*
