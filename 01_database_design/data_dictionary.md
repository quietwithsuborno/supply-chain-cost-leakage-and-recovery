# BCPL Cost Leakage Diagnostic — Data Dictionary

**Project:** Supply Chain Cost Leakage & Recovery Plan  
**Company:** Bongo Consumer Products Ltd. (BCPL) — Fictional Bangladeshi FMCG  
**Database:** `BCPL_CostLeakage`  
**Last Updated:** Day 4

---

## 📌 Table of Contents

1. [dim_supplier](#dim_supplier)
2. [dim_product](#dim_product)
3. [dim_warehouse](#dim_warehouse)
4. [dim_route](#dim_route)
5. [dim_date](#dim_date)
6. [fact_purchase_orders](#fact_purchase_orders)
7. [fact_inventory_snapshot](#fact_inventory_snapshot)
8. [fact_shipments](#fact_shipments)
9. [fact_order_fulfillment](#fact_order_fulfillment)

---

## dim_supplier

Stores master information about all raw material and packaging suppliers contracted with BCPL.

| Column | Data Type | Key | Description |
|---|---|---|---|
| `supplier_id` | VARCHAR(10) | PK | Unique supplier identifier (e.g. SUP-001) |
| `supplier_name` | VARCHAR(100) | — | Supplier company name |
| `category` | VARCHAR(50) | — | Supplier category: `Packaging` / `Raw Material` |
| `sub_category` | VARCHAR(50) | — | Sub-category: `Chemical` / `Food` / `Personal Care` |
| `location` | VARCHAR(100) | — | Supplier location (city/country) |
| `supplier_type` | VARCHAR(20) | — | `Local` / `Import` |
| `contract_start` | DATE | — | Date when supplier contract with BCPL began |
| `standard_lead_days` | INT | — | Agreed delivery lead time in days |

---

## dim_product

Stores master information about all 30 SKUs manufactured/sold by BCPL across 3 product categories.

| Column | Data Type | Key | Description |
|---|---|---|---|
| `product_id` | VARCHAR(10) | PK | Unique product identifier (e.g. PRD-001) |
| `product_name` | VARCHAR(100) | — | Product name |
| `category` | VARCHAR(50) | — | `Personal Care` / `Home Care` / `Packaged Food` |
| `unit_of_measure` | VARCHAR(20) | — | `KG` / `Litre` / `Piece` |
| `standard_cost` | DECIMAL(10,2) | — | Standard/budgeted unit cost in ৳ |
| `reorder_level` | INT | — | Minimum stock level before reorder is triggered |
| `max_stock_level` | INT | — | Maximum allowed stock level |

---

## dim_warehouse

Stores information about BCPL's 4 warehouses across Bangladesh.

| Column | Data Type | Key | Description |
|---|---|---|---|
| `warehouse_name` | VARCHAR(100) | — | Warehouse name |
| `location` | VARCHAR(100) | — | City where warehouse is located |
| `type` | VARCHAR(20) | — | `Central` / `Regional` |
| `capacity_units` | INT | — | Maximum storage capacity in units |
| `monthly_holding_rate` | DECIMAL(5,4) | — | Monthly holding cost rate (e.g. `0.0200` = 2%) |
| `warehouse_id` | VARCHAR(10) | PK | Unique warehouse identifier (e.g. WH-01) |

---

## dim_route

Stores information about BCPL's 6 distribution routes connecting warehouses to distributors.

| Column | Data Type | Key | Description |
|---|---|---|---|
| `route_id` | VARCHAR(10) | PK | Unique route identifier (e.g. RT-01) |
| `route_name` | VARCHAR(100) | — | Descriptive route name |
| `origin_warehouse` | VARCHAR(10) | FK → dim_warehouse | Warehouse from which shipment originates |
| `destination` | VARCHAR(100) | — | Delivery destination description |
| `route_type` | VARCHAR(20) | — | `Urban` / `Inter-city` / `Rural` |
| `planned_distance_km` | DECIMAL(8,2) | — | Standard planned distance in KM |
| `cost_per_km` | DECIMAL(8,2) | — | Standard freight cost per KM (default: ৳12.00) |

---

## dim_date

Date dimension table supporting time-based analysis across all fact tables.

| Column | Data Type | Key | Description |
|---|---|---|---|
| `date_id` | DATE | PK | Date value in YYYY-MM-DD format |
| `day` | INT | — | Day of month (1–31) |
| `month` | INT | — | Month number (1–12) |
| `month_name` | VARCHAR(20) | — | Month name (e.g. January) |
| `quarter` | INT | — | Quarter number (1–4) |
| `year` | INT | — | Year (e.g. 2024) |
| `day_of_week` | VARCHAR(20) | — | Day name (e.g. Monday) |
| `is_weekend` | BIT | — | `1` = weekend, `0` = weekday |

---

## fact_purchase_orders

Records all purchase orders placed by BCPL with suppliers. Core table for **Procurement Leakage** analysis.

| Column | Data Type | Key | Description | Leakage Role |
|---|---|---|---|---|
| `po_id` | VARCHAR(15) | PK | Purchase order ID (e.g. PO-2024-0001) | — |
| `supplier_id` | VARCHAR(10) | FK → dim_supplier | Supplier who received the PO | — |
| `product_id` | VARCHAR(10) | FK → dim_product | Product ordered | — |
| `order_date` | DATE | — | Actual date PO was placed | — |
| `date_id` | DATE | FK → dim_date | Date dimension join key | — |
| `quantity_ordered` | INT | — | Units ordered | — |
| `standard_unit_price` | DECIMAL(10,2) | — | Agreed/budgeted price per unit in ৳ | Leakage baseline |
| `actual_unit_price` | DECIMAL(10,2) | — | Actually paid price per unit in ৳ | Leakage source |
| `order_type` | VARCHAR(20) | — | `Regular` / `Rush` / `Emergency` | Rush = premium cost |
| `delivery_date` | DATE | — | Expected delivery date | — |
| `po_status` | VARCHAR(20) | — | `Completed` / `Pending` / `Cancelled` | — |

**Leakage Formula:**
```
Procurement Leakage (per order) = (actual_unit_price − standard_unit_price) × quantity_ordered
Procurement Leakage % = (actual_unit_price − standard_unit_price) / standard_unit_price × 100
Flag: % Variance > 5% = leakage flagged
```

---

## fact_inventory_snapshot

Monthly stock snapshot per product per warehouse. Core table for **Inventory Leakage** analysis.

| Column | Data Type | Key | Description | Leakage Role |
|---|---|---|---|---|
| `snapshot_id` | VARCHAR(15) | PK | Unique snapshot record ID | — |
| `product_id` | VARCHAR(10) | FK → dim_product | Product being snapshotted | — |
| `date_id` | DATE | FK → dim_date | Date dimension join key | — |
| `warehouse_id` | VARCHAR(10) | FK → dim_warehouse | Warehouse location of stock | — |
| `snapshot_date` | DATE | — | Month-end snapshot date | — |
| `opening_stock` | INT | — | Stock units at start of month | — |
| `closing_stock` | INT | — | Stock units at end of month | — |
| `avg_stock_value` | DECIMAL(12,2) | — | Average stock value in ৳ for the month | Holding cost base |
| `stock_age_days` | INT | — | Days since product last moved | Dead stock flag |
| `is_dead_stock` | BIT | — | `1` if stock_age_days > 90 | Leakage flag |
| `holding_cost` | DECIMAL(10,2) | — | avg_stock_value × monthly_holding_rate | Leakage source |

**Leakage Formula:**
```
Inventory Leakage = SUM(holding_cost) WHERE is_dead_stock = 1
Flag: stock_age_days > 90 = dead stock flagged
```

---

## fact_shipments

Records all outbound shipments from BCPL warehouses. Core table for **Logistics Leakage** analysis.

| Column | Data Type | Key | Description | Leakage Role |
|---|---|---|---|---|
| `shipment_id` | VARCHAR(15) | PK | Shipment ID (e.g. SHP-2024-0001) | — |
| `route_id` | VARCHAR(10) | FK → dim_route | Route taken for this shipment | — |
| `date_id` | DATE | FK → dim_date | Date dimension join key | — |
| `shipment_date` | DATE | — | Actual dispatch date | — |
| `warehouse_id` | VARCHAR(10) | FK → dim_warehouse | Origin warehouse | — |
| `planned_freight_cost` | DECIMAL(10,2) | — | Budgeted freight cost in ৳ | Leakage baseline |
| `actual_freight_cost` | DECIMAL(10,2) | — | Actually paid freight cost in ৳ | Leakage source |
| `planned_distance_km` | DECIMAL(8,2) | — | Standard route distance in KM | — |
| `actual_distance_km` | DECIMAL(8,2) | — | Actual distance travelled in KM | Route inefficiency |
| `delivery_status` | VARCHAR(20) | — | `On-Time` / `Late` / `Failed` | Late = penalty |
| `late_penalty` | DECIMAL(10,2) | — | ৳500 if Late, ৳0 otherwise | Leakage source |

**Leakage Formula:**
```
Logistics Leakage = SUM(actual_freight_cost − planned_freight_cost) + SUM(late_penalty)
Flag: Cost overrun > 10% = leakage flagged
```

---

## fact_order_fulfillment

Records fulfillment outcome for each purchase order. Core table for **Fulfillment Leakage** analysis.

| Column | Data Type | Key | Description | Leakage Role |
|---|---|---|---|---|
| `fulfillment_id` | VARCHAR(15) | PK | Unique fulfillment record ID | — |
| `po_id` | VARCHAR(15) | FK → fact_purchase_orders | Linked purchase order | — |
| `warehouse_id` | VARCHAR(10) | FK → dim_warehouse | Fulfilling warehouse | — |
| `fulfillment_date` | DATE | — | Date order was fulfilled | — |
| `date_id` | DATE | FK → dim_date | Date dimension join key | — |
| `order_status` | VARCHAR(20) | — | `Complete` / `Partial` / `Returned` | — |
| `is_return` | BIT | — | `1` = returned order | Leakage flag |
| `return_reason` | VARCHAR(100) | — | Reason for return (if applicable) | — |
| `return_cost` | DECIMAL(10,2) | — | ৳300 if returned, ৳0 otherwise | Leakage source |
| `is_partial` | BIT | — | `1` = partial shipment | Leakage flag |
| `partial_extra_cost` | DECIMAL(10,2) | — | ৳800 if partial, ৳0 otherwise | Leakage source |

**Leakage Formula:**
```
Fulfillment Leakage = SUM(return_cost) + SUM(partial_extra_cost)
Flag: Return rate > 3% = leakage flagged
```

---

## 📌 Cost Assumption Notes

> All cost assumptions below are illustrative estimates used to quantify leakage magnitude. In a real engagement, these rates would be validated with finance/operations teams.

| Assumption | Value | Used In |
|---|---|---|
| Monthly inventory holding rate | 2% of avg stock value | fact_inventory_snapshot |
| Dead stock threshold | > 90 days without movement | fact_inventory_snapshot |
| Late delivery penalty | ৳500 per late shipment | fact_shipments |
| Standard freight cost | ৳12.00 per KM | dim_route |
| Return processing cost | ৳300 per returned order | fact_order_fulfillment |
| Partial shipment extra cost | ৳800 per partial trip | fact_order_fulfillment |
| Procurement leakage flag threshold | > 5% price variance | fact_purchase_orders |
| Logistics leakage flag threshold | > 10% cost overrun | fact_shipments |
| Fulfillment leakage flag threshold | Return rate > 3% | fact_order_fulfillment |
