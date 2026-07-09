# Data Cleaning Summary

## Overview
Raw data was intentionally injected with quality issues to simulate 
real-world messiness, then cleaned using a Python pipeline.

---

## Before vs After

| Table | Raw Rows | Clean Rows | Removed |
|---|---|---|---|
| fact_purchase_orders | 1,248 | 1,200 | 48 |
| fact_inventory_snapshot | 1,483 | 1,440 | 43 |
| fact_shipments | 832 | 800 | 32 |
| fact_order_fulfillment | 1,094 | 1,062 | 32 |

---

## Issues Cleaned

| Issue Type | Tables Affected | Action Taken |
|---|---|---|
| Duplicate records | All 4 fact tables | Removed — kept first occurrence |
| Mixed date formats (DD-MM-YYYY, MM/DD/YYYY) | All 4 fact tables | Standardized to YYYY-MM-DD |
| ID format inconsistency (SUP001, sup-001) | PO, Inventory, Fulfillment | Standardized to SUP-001 format |
| Negative values (cost, penalty) | PO, Inventory, Shipments, Fulfillment | Converted to absolute value |
| Outliers (quantity, stock, freight) | PO, Inventory, Shipments | Replaced with column median |
| Extra whitespace in text fields | All 4 fact tables | Stripped |
| Mixed text casing (COMPLETED, completed) | PO, Shipments, Fulfillment | Title Case applied |
| Null values | All 4 fact tables | Context-aware fill (median/mode/logic) |

---

## Validation Results (post-cleaning)

All 6 checks passed via `validate_data.py`:

- ✅ Row counts match expected
- ✅ Zero null values
- ✅ Zero duplicate primary keys
- ✅ Zero referential integrity violations
- ✅ Zero ID format violations
- ✅ Zero business logic violations

---

## Pipeline
Full pipeline reproducible via: `python main.py`
