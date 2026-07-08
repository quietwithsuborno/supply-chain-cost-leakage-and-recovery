import pandas as pd
import numpy as np
import os
import shutil

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
CLEANED_DIR = "../05_data/cleaned"
RAW_DIR     = "../05_data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

np.random.seed(99)

# ─────────────────────────────────────────
# LOAD CLEAN FACT TABLES
# ─────────────────────────────────────────
po       = pd.read_csv(f"{CLEANED_DIR}/fact_purchase_orders.csv")
inv      = pd.read_csv(f"{CLEANED_DIR}/fact_inventory_snapshot.csv")
shp      = pd.read_csv(f"{CLEANED_DIR}/fact_shipments.csv")
ful      = pd.read_csv(f"{CLEANED_DIR}/fact_order_fulfillment.csv")

print("📦 Loaded clean data:")
print(f"  fact_purchase_orders:    {len(po)} rows")
print(f"  fact_inventory_snapshot: {len(inv)} rows")
print(f"  fact_shipments:          {len(shp)} rows")
print(f"  fact_order_fulfillment:  {len(ful)} rows")

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def random_idx(df, frac):
    return df.sample(frac=frac).index

def inject_nulls(df, col, frac):
    idx = random_idx(df, frac)
    df.loc[idx, col] = np.nan
    return len(idx)

def inject_date_format_mix(df, col, frac):
    """Mix 3 date formats in same column"""
    idx = random_idx(df, frac)
    for i in idx:
        val = df.loc[i, col]
        if pd.isna(val):
            continue
        try:
            d = pd.to_datetime(val)
            fmt = np.random.choice(["dd-mm-yyyy", "mm/dd/yyyy"])
            if fmt == "dd-mm-yyyy":
                df.loc[i, col] = d.strftime("%d-%m-%Y")
            else:
                df.loc[i, col] = d.strftime("%m/%d/%Y")
        except:
            pass
    return len(idx)

def inject_duplicates(df, frac):
    dups = df.sample(frac=frac)
    result = pd.concat([df, dups], ignore_index=True)
    return result, len(dups)

def inject_text_case_mix(df, col, frac):
    """Mix UPPER, lower, Title case"""
    idx = random_idx(df, frac)
    for i in idx:
        val = df.loc[i, col]
        if pd.isna(val):
            continue
        choice = np.random.choice(["upper", "lower"])
        df.loc[i, col] = val.upper() if choice == "upper" else val.lower()
    return len(idx)

def inject_id_format_mix(df, col, frac):
    """SUP-001 → SUP001 or sup-001"""
    idx = random_idx(df, frac)
    for i in idx:
        val = df.loc[i, col]
        if pd.isna(val):
            continue
        choice = np.random.choice(["no_dash", "lowercase"])
        if choice == "no_dash":
            df.loc[i, col] = val.replace("-", "")
        else:
            df.loc[i, col] = val.lower()
    return len(idx)

def inject_outliers(df, col, frac, multiplier=100):
    idx = random_idx(df, frac)
    df.loc[idx, col] = df.loc[idx, col] * multiplier
    return len(idx)

def inject_negative_values(df, col, frac):
    idx = random_idx(df, frac)
    df.loc[idx, col] = df.loc[idx, col].abs() * -1
    return len(idx)

def inject_whitespace(df, col, frac):
    idx = random_idx(df, frac)
    for i in idx:
        val = df.loc[i, col]
        if pd.isna(val):
            continue
        df.loc[i, col] = "  " + str(val) + "  "
    return len(idx)

# ─────────────────────────────────────────
# 1. MESS UP fact_purchase_orders
# ─────────────────────────────────────────
print("\n🔥 Injecting messiness into fact_purchase_orders...")
po_messy = po.copy()
log = {}

log["null_delivery_date"]      = inject_nulls(po_messy, "delivery_date", 0.05)
log["null_actual_unit_price"]  = inject_nulls(po_messy, "actual_unit_price", 0.04)
log["null_order_type"]         = inject_nulls(po_messy, "order_type", 0.03)
log["date_format_order_date"]  = inject_date_format_mix(po_messy, "order_date", 0.15)
log["id_format_supplier_id"]   = inject_id_format_mix(po_messy, "supplier_id", 0.08)
log["id_format_product_id"]    = inject_id_format_mix(po_messy, "product_id", 0.06)
log["outlier_quantity"]        = inject_outliers(po_messy, "quantity_ordered", 0.02)
log["negative_actual_price"]   = inject_negative_values(po_messy, "actual_unit_price", 0.02)
log["whitespace_order_type"]   = inject_whitespace(po_messy, "order_type", 0.05)
log["case_mix_po_status"]      = inject_text_case_mix(po_messy, "po_status", 0.10)
po_messy, log["duplicates"]    = inject_duplicates(po_messy, 0.04)

for k, v in log.items():
    print(f"  ✓ {k}: {v} records affected")

# ─────────────────────────────────────────
# 2. MESS UP fact_inventory_snapshot
# ─────────────────────────────────────────
print("\n🔥 Injecting messiness into fact_inventory_snapshot...")
inv_messy = inv.copy()
log2 = {}

log2["null_avg_stock_value"]    = inject_nulls(inv_messy, "avg_stock_value", 0.05)
log2["null_stock_age_days"]     = inject_nulls(inv_messy, "stock_age_days", 0.04)
log2["null_holding_cost"]       = inject_nulls(inv_messy, "holding_cost", 0.04)
log2["date_format_snapshot"]    = inject_date_format_mix(inv_messy, "snapshot_date", 0.12)
log2["id_format_product_id"]    = inject_id_format_mix(inv_messy, "product_id", 0.07)
log2["id_format_warehouse_id"]  = inject_id_format_mix(inv_messy, "warehouse_id", 0.06)
log2["outlier_closing_stock"]   = inject_outliers(inv_messy, "closing_stock", 0.02)
log2["negative_holding_cost"]   = inject_negative_values(inv_messy, "holding_cost", 0.02)
log2["whitespace_warehouse_id"] = inject_whitespace(inv_messy, "warehouse_id", 0.04)
inv_messy, log2["duplicates"]   = inject_duplicates(inv_messy, 0.03)

for k, v in log2.items():
    print(f"  ✓ {k}: {v} records affected")

# ─────────────────────────────────────────
# 3. MESS UP fact_shipments
# ─────────────────────────────────────────
print("\n🔥 Injecting messiness into fact_shipments...")
shp_messy = shp.copy()
log3 = {}

log3["null_actual_freight"]     = inject_nulls(shp_messy, "actual_freight_cost", 0.05)
log3["null_delivery_status"]    = inject_nulls(shp_messy, "delivery_status", 0.04)
log3["null_actual_distance"]    = inject_nulls(shp_messy, "actual_distance_km", 0.04)
log3["date_format_shipment"]    = inject_date_format_mix(shp_messy, "shipment_date", 0.15)
log3["id_format_route_id"]      = inject_id_format_mix(shp_messy, "route_id", 0.08)
log3["id_format_warehouse_id"]  = inject_id_format_mix(shp_messy, "warehouse_id", 0.06)
log3["outlier_actual_freight"]  = inject_outliers(shp_messy, "actual_freight_cost", 0.02)
log3["negative_late_penalty"]   = inject_negative_values(shp_messy, "late_penalty", 0.02)
log3["case_mix_delivery_status"]= inject_text_case_mix(shp_messy, "delivery_status", 0.10)
log3["whitespace_route_id"]     = inject_whitespace(shp_messy, "route_id", 0.05)
shp_messy, log3["duplicates"]   = inject_duplicates(shp_messy, 0.04)

for k, v in log3.items():
    print(f"  ✓ {k}: {v} records affected")

# ─────────────────────────────────────────
# 4. MESS UP fact_order_fulfillment
# ─────────────────────────────────────────
print("\n🔥 Injecting messiness into fact_order_fulfillment...")
ful_messy = ful.copy()
log4 = {}

log4["null_return_reason"]       = inject_nulls(ful_messy, "return_reason", 0.06)
log4["null_fulfillment_date"]    = inject_nulls(ful_messy, "fulfillment_date", 0.04)
log4["null_partial_extra_cost"]  = inject_nulls(ful_messy, "partial_extra_cost", 0.04)
log4["date_format_fulfillment"]  = inject_date_format_mix(ful_messy, "fulfillment_date", 0.12)
log4["id_format_warehouse_id"]   = inject_id_format_mix(ful_messy, "warehouse_id", 0.07)
log4["id_format_po_id"]          = inject_id_format_mix(ful_messy, "po_id", 0.05)
log4["case_mix_order_status"]    = inject_text_case_mix(ful_messy, "order_status", 0.10)
log4["negative_return_cost"]     = inject_negative_values(ful_messy, "return_cost", 0.02)
log4["whitespace_order_status"]  = inject_whitespace(ful_messy, "order_status", 0.05)
ful_messy, log4["duplicates"]    = inject_duplicates(ful_messy, 0.03)

for k, v in log4.items():
    print(f"  ✓ {k}: {v} records affected")

# ─────────────────────────────────────────
# EXPORT MESSY FILES TO raw/
# ─────────────────────────────────────────
po_messy.to_csv(f"{RAW_DIR}/raw_purchase_orders.csv",       index=False)
inv_messy.to_csv(f"{RAW_DIR}/raw_inventory_snapshot.csv",   index=False)
shp_messy.to_csv(f"{RAW_DIR}/raw_shipments.csv",            index=False)
ful_messy.to_csv(f"{RAW_DIR}/raw_order_fulfillment.csv",    index=False)

print("\n📊 Final messy row counts:")
print(f"  raw_purchase_orders:    {len(po_messy)} rows  (was {len(po)})")
print(f"  raw_inventory_snapshot: {len(inv_messy)} rows (was {len(inv)})")
print(f"  raw_shipments:          {len(shp_messy)} rows  (was {len(shp)})")
print(f"  raw_order_fulfillment:  {len(ful_messy)} rows (was {len(ful)})")

print("\n🎉 All messy CSVs saved to:", RAW_DIR)