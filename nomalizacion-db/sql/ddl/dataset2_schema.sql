-- ============================================================
-- DDL: E-commerce Sales Data — Tabla DESNORMALIZADA original
-- Esta tabla replica exactamente el CSV crudo.
-- El script normalize_dataset2.py la leerá y generará
-- las 5 tablas en 3FN (countries, customers, products,
-- invoices, invoice_items).
-- ============================================================

DROP TABLE IF EXISTS ecommerce_raw CASCADE;

CREATE TABLE ecommerce_raw (
    invoice_no    VARCHAR(20),
    stock_code    VARCHAR(20),
    description   VARCHAR(255),
    quantity      INTEGER,
    invoice_date  VARCHAR(30),
    unit_price    NUMERIC(10,2),
    customer_id   INTEGER,
    country       VARCHAR(100)
);
