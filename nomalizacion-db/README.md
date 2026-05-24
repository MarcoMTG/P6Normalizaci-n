# Normalización de Bases de Datos — Práctica 6
## Dataset 2: E-commerce Sales Data

**ESCOM — IPN | Bases de Datos 2020**

---

## Descripción

Este proyecto implementa la normalización completa (hasta 3FN) del dataset
de e-commerce de Kaggle, automatizada mediante Python.

## Estructura del Proyecto

```
normalizacion-db/
├── data/
│   ├── raw/
│   │   └── data.csv                  ← Dataset original (541,909 filas)
│   └── normalized/
│       └── ecommerce/
│           ├── countries.csv          ← 37 filas
│           ├── customers.csv          ← 4,372 filas
│           ├── products.csv           ← 3,684 filas
│           ├── invoices.csv           ← 22,190 filas
│           ├── invoice_items.csv      ← 406,829 filas
│           └── ecommerce_3fn.db       ← Base de datos SQLite lista para usar
│
├── scripts/
│   ├── utils.py                       ← Funciones auxiliares reutilizables
│   └── normalize_dataset2.py          ← Script principal de normalización
│
├── sql/
│   ├── ddl/
│   │   └── dataset2_schema.sql        ← CREATE TABLE (esquema 3FN)
│   └── dml/
│       └── dataset2_data.sql          ← INSERT muestra (200 filas por tabla)
│
├── docs/
│   └── analisis_normalizacion.md      ← Documento completo de análisis
│
├── requirements.txt
└── README.md
```

## Instalación y Uso

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar normalización
python scripts/normalize_dataset2.py
```

## Modelo Normalizado (3FN)

```
countries ──1:N──► customers ──1:N──► invoices ──1:N──► invoice_items ◄──N:1── products
```

## Resultados

| Tabla | Filas |
|---|---|
| countries | 37 |
| customers | 4,372 |
| products | 3,684 |
| invoices | 22,190 |
| invoice_items | 406,829 |

**Reducción de redundancia: ~51%**
