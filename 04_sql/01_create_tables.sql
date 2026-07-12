-- ══════════════════════════════════════════════════
-- BCPL Cost Leakage Diagnostic
-- Database & Table Creation Script
-- ══════════════════════════════════════════════════

-- Step 1: Create Database
CREATE DATABASE BCPL_CostLeakage;
GO

USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- DIMENSION TABLES
-- ══════════════════════════════════════════════════

CREATE TABLE dim_supplier (
    supplier_id         VARCHAR(10)     NOT NULL,
    supplier_name       VARCHAR(100)    NOT NULL,
    category            VARCHAR(50)     NOT NULL,
    sub_category        VARCHAR(50)     NOT NULL,
    location            VARCHAR(100)    NOT NULL,
    supplier_type       VARCHAR(20)     NOT NULL,
    contract_start      DATE            NOT NULL,
    standard_lead_days  INT             NOT NULL,
    CONSTRAINT PK_dim_supplier PRIMARY KEY (supplier_id)
);

CREATE TABLE dim_product (
    product_id          VARCHAR(10)     NOT NULL,
    product_name        VARCHAR(100)    NOT NULL,
    category            VARCHAR(50)     NOT NULL,
    unit_of_measure     VARCHAR(20)     NOT NULL,
    standard_cost       DECIMAL(10,2)   NOT NULL,
    reorder_level       INT             NOT NULL,
    max_stock_level     INT             NOT NULL,
    CONSTRAINT PK_dim_product PRIMARY KEY (product_id)
);

CREATE TABLE dim_warehouse (
    warehouse_id            VARCHAR(10)     NOT NULL,
    warehouse_name          VARCHAR(100)    NOT NULL,
    location                VARCHAR(100)    NOT NULL,
    type                    VARCHAR(20)     NOT NULL,
    capacity_units          INT             NOT NULL,
    monthly_holding_rate    DECIMAL(5,4)    NOT NULL,
    CONSTRAINT PK_dim_warehouse PRIMARY KEY (warehouse_id)
);

CREATE TABLE dim_route (
    route_id                VARCHAR(10)     NOT NULL,
    route_name              VARCHAR(100)    NOT NULL,
    origin_warehouse        VARCHAR(10)     NOT NULL,
    destination             VARCHAR(100)    NOT NULL,
    route_type              VARCHAR(20)     NOT NULL,
    planned_distance_km     DECIMAL(8,2)    NOT NULL,
    cost_per_km             DECIMAL(8,2)    NOT NULL,
    CONSTRAINT PK_dim_route PRIMARY KEY (route_id),
    CONSTRAINT FK_route_warehouse FOREIGN KEY (origin_warehouse)
        REFERENCES dim_warehouse(warehouse_id)
);

CREATE TABLE dim_date (
    date_id         DATE            NOT NULL,
    day             INT             NOT NULL,
    month           INT             NOT NULL,
    month_name      VARCHAR(20)     NOT NULL,
    quarter         INT             NOT NULL,
    year            INT             NOT NULL,
    day_of_week     VARCHAR(20)     NOT NULL,
    is_weekend      BIT             NOT NULL,
    CONSTRAINT PK_dim_date PRIMARY KEY (date_id)
);

-- ══════════════════════════════════════════════════
-- FACT TABLES
-- ══════════════════════════════════════════════════

CREATE TABLE fact_purchase_orders (
    po_id                   VARCHAR(15)     NOT NULL,
    supplier_id             VARCHAR(10)     NOT NULL,
    product_id              VARCHAR(10)     NOT NULL,
    order_date              DATE            NOT NULL,
    date_id                 DATE            NOT NULL,
    quantity_ordered        INT             NOT NULL,
    standard_unit_price     DECIMAL(10,2)   NOT NULL,
    actual_unit_price       DECIMAL(10,2)   NOT NULL,
    order_type              VARCHAR(20)     NOT NULL,
    delivery_date           DATE            NOT NULL,
    po_status               VARCHAR(20)     NOT NULL,
    CONSTRAINT PK_fact_po PRIMARY KEY (po_id),
    CONSTRAINT FK_po_supplier FOREIGN KEY (supplier_id)
        REFERENCES dim_supplier(supplier_id),
    CONSTRAINT FK_po_product FOREIGN KEY (product_id)
        REFERENCES dim_product(product_id),
    CONSTRAINT FK_po_date FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

CREATE TABLE fact_inventory_snapshot (
    snapshot_id         VARCHAR(15)     NOT NULL,
    product_id          VARCHAR(10)     NOT NULL,
    date_id             DATE            NOT NULL,
    warehouse_id        VARCHAR(10)     NOT NULL,
    snapshot_date       DATE            NOT NULL,
    opening_stock       INT             NOT NULL,
    closing_stock       INT             NOT NULL,
    avg_stock_value     DECIMAL(12,2)   NOT NULL,
    stock_age_days      INT             NOT NULL,
    is_dead_stock       BIT             NOT NULL,
    holding_cost        DECIMAL(10,2)   NOT NULL,
    CONSTRAINT PK_fact_inv PRIMARY KEY (snapshot_id),
    CONSTRAINT FK_inv_product FOREIGN KEY (product_id)
        REFERENCES dim_product(product_id),
    CONSTRAINT FK_inv_warehouse FOREIGN KEY (warehouse_id)
        REFERENCES dim_warehouse(warehouse_id),
    CONSTRAINT FK_inv_date FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

CREATE TABLE fact_shipments (
    shipment_id             VARCHAR(15)     NOT NULL,
    route_id                VARCHAR(10)     NOT NULL,
    date_id                 DATE            NOT NULL,
    shipment_date           DATE            NOT NULL,
    warehouse_id            VARCHAR(10)     NOT NULL,
    planned_freight_cost    DECIMAL(10,2)   NOT NULL,
    actual_freight_cost     DECIMAL(10,2)   NOT NULL,
    planned_distance_km     DECIMAL(8,2)    NOT NULL,
    actual_distance_km      DECIMAL(8,2)    NOT NULL,
    delivery_status         VARCHAR(20)     NOT NULL,
    late_penalty            DECIMAL(10,2)   NOT NULL,
    CONSTRAINT PK_fact_shp PRIMARY KEY (shipment_id),
    CONSTRAINT FK_shp_route FOREIGN KEY (route_id)
        REFERENCES dim_route(route_id),
    CONSTRAINT FK_shp_warehouse FOREIGN KEY (warehouse_id)
        REFERENCES dim_warehouse(warehouse_id),
    CONSTRAINT FK_shp_date FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

CREATE TABLE fact_order_fulfillment (
    fulfillment_id      VARCHAR(15)     NOT NULL,
    po_id               VARCHAR(15)     NOT NULL,
    warehouse_id        VARCHAR(10)     NOT NULL,
    fulfillment_date    DATE            NOT NULL,
    date_id             DATE            NOT NULL,
    order_status        VARCHAR(20)     NOT NULL,
    is_return           BIT             NOT NULL,
    return_reason       VARCHAR(100)    NULL,
    return_cost         DECIMAL(10,2)   NOT NULL,
    is_partial          BIT             NOT NULL,
    partial_extra_cost  DECIMAL(10,2)   NOT NULL,
    CONSTRAINT PK_fact_ful PRIMARY KEY (fulfillment_id),
    CONSTRAINT FK_ful_po FOREIGN KEY (po_id)
        REFERENCES fact_purchase_orders(po_id),
    CONSTRAINT FK_ful_warehouse FOREIGN KEY (warehouse_id)
        REFERENCES dim_warehouse(warehouse_id),
    CONSTRAINT FK_ful_date FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);

-- ══════════════════════════════════════════════════
-- VERIFY
-- ══════════════════════════════════════════════════
SELECT
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'BCPL_CostLeakage'
ORDER BY TABLE_TYPE, TABLE_NAME;