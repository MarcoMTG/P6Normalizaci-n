-- ============================================================
-- DDL: E-commerce Sales Data — Esquema 3FN
-- Dataset 2 | Práctica 6: Normalización de Bases de Datos
-- ============================================================

DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS products;

-- Países
CREATE TABLE countries (
    country_id   INTEGER      PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

-- Clientes
CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    country_id   INTEGER NOT NULL,
    CONSTRAINT fk_customers_country
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Productos
CREATE TABLE products (
    stock_code  VARCHAR(20)  PRIMARY KEY,
    description VARCHAR(255)
);

-- Facturas / Pedidos
CREATE TABLE invoices (
    invoice_no    VARCHAR(20)  PRIMARY KEY,
    customer_id   INTEGER      NOT NULL,
    invoice_date  DATETIME     NOT NULL,
    CONSTRAINT fk_invoices_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Líneas de detalle de cada factura
CREATE TABLE invoice_items (
    item_id     INTEGER       PRIMARY KEY AUTOINCREMENT,
    invoice_no  VARCHAR(20)   NOT NULL,
    stock_code  VARCHAR(20)   NOT NULL,
    quantity    INTEGER        NOT NULL,
    unit_price  DECIMAL(10,2)  NOT NULL,
    CONSTRAINT fk_items_invoice
        FOREIGN KEY (invoice_no) REFERENCES invoices(invoice_no),
    CONSTRAINT fk_items_product
        FOREIGN KEY (stock_code) REFERENCES products(stock_code)
);
