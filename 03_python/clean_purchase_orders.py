import pandas as pd
import numpy as np
import os
import re

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
RAW_DIR     = "../05_data/raw"
CLEANED_DIR = "../05_data/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)

# ─────────────────────────────────────────
# LOAD MESSY DATA
# ─────────────────────────────────────────
df = pd.read_csv(f"{RAW_DIR}/raw_purchase_orders.csv")
original_rows = len(df)
print(f"📦 Loaded raw_purchase_orders: {original_rows} rows")

# ─────────────────────────────────────────
# STEP 1: Remove Duplicates
# ─────────────────────────────────────────
before = len(df)
df = df.drop_duplicates(subset=["po_id"], keep="first")
dupes_removed = before - len(df)
print(f"\n✅ Step 1 — Duplicates removed: {dupes_removed}")

# ─────────────────────────────────────────
# STEP 2: Standardize ID Format
# SUP001 / sup-001 → SUP-001
# PRD001 / prd-001 → PRD-001
# PO2024001 / po-2024-001 → PO-2024-001
# ─────────────────────────────────────────
def fix_supplier_id(val):
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "")
    # Remove all dashes first, then reformat
    val = val.replace("-", "")
    if val.startswith("SUP") and len(val) == 6:
        return f"SUP-{val[3:]}"
    return val

def fix_product_id(val):
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "")
    val = val.replace("-", "")
    if val.startswith("PRD") and len(val) == 6:
        return f"PRD-{val[3:]}"
    return val

df["supplier_id"] = df["supplier_id"].apply(fix_supplier_id)
df["product_id"]  = df["product_id"].apply(fix_product_id)

sup_fixed = df["supplier_id"].str.match(r"SUP-\d{3}").sum()
prd_fixed = df["product_id"].str.match(r"PRD-\d{3}").sum()
print(f"\n✅ Step 2 — ID format standardized:")
print(f"   supplier_id valid format: {sup_fixed}/{len(df)}")
print(f"   product_id  valid format: {prd_fixed}/{len(df)}")

# ─────────────────────────────────────────
# STEP 3: Standardize Date Format → YYYY-MM-DD
# ─────────────────────────────────────────
def parse_date(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]:
        try:
            return pd.to_datetime(val, format=fmt).strftime("%Y-%m-%d")
        except:
            continue
    return np.nan

df["order_date"]    = df["order_date"].apply(parse_date)
df["delivery_date"] = df["delivery_date"].apply(parse_date)
df["date_id"]       = df["date_id"].apply(parse_date)

null_order    = df["order_date"].isna().sum()
null_delivery = df["delivery_date"].isna().sum()
print(f"\n✅ Step 3 — Date format standardized:")
print(f"   order_date nulls remaining:    {null_order}")
print(f"   delivery_date nulls remaining: {null_delivery}")

# ─────────────────────────────────────────
# STEP 4: Clean Text Columns
# Strip whitespace + Title Case
# ─────────────────────────────────────────
def clean_text(val):
    if pd.isna(val):
        return val
    return str(val).strip().title()

df["order_type"] = df["order_type"].apply(clean_text)
df["po_status"]  = df["po_status"].apply(clean_text)

# Validate allowed values
valid_order_types = ["Regular", "Rush", "Emergency"]
valid_po_status   = ["Completed", "Pending", "Cancelled"]

invalid_order_type = (~df["order_type"].isin(valid_order_types) & df["order_type"].notna()).sum()
invalid_po_status  = (~df["po_status"].isin(valid_po_status) & df["po_status"].notna()).sum()

print(f"\n✅ Step 4 — Text columns cleaned:")
print(f"   Invalid order_type values remaining: {invalid_order_type}")
print(f"   Invalid po_status values remaining:  {invalid_po_status}")

# ─────────────────────────────────────────
# STEP 5: Fix Negative Values
# actual_unit_price < 0 → take absolute value
# ─────────────────────────────────────────
neg_price = (df["actual_unit_price"] < 0).sum()
df.loc[df["actual_unit_price"] < 0, "actual_unit_price"] = df["actual_unit_price"].abs()
print(f"\n✅ Step 5 — Negative prices fixed: {neg_price}")

# ─────────────────────────────────────────
# STEP 6: Fix Outliers in quantity_ordered
# Any quantity > 2000 is unrealistic for BCPL
# ─────────────────────────────────────────
outlier_qty = (df["quantity_ordered"] > 2000).sum()
# Replace with median quantity
median_qty  = df.loc[df["quantity_ordered"] <= 2000, "quantity_ordered"].median()
df.loc[df["quantity_ordered"] > 2000, "quantity_ordered"] = int(median_qty)
print(f"\n✅ Step 6 — Outlier quantities fixed: {outlier_qty} (replaced with median: {int(median_qty)})")

# ─────────────────────────────────────────
# STEP 7: Handle Remaining Nulls
# ─────────────────────────────────────────
# actual_unit_price null → fill with standard_unit_price (safe assumption)
null_actual = df["actual_unit_price"].isna().sum()
df["actual_unit_price"] = df["actual_unit_price"].fillna(df["standard_unit_price"])

# order_type null → fill with "Regular" (most common, safe default)
null_order_type = df["order_type"].isna().sum()
df["order_type"] = df["order_type"].fillna("Regular")

# delivery_date null → fill with order_date + 10 days (avg lead time)
null_del = df["delivery_date"].isna().sum()
df["delivery_date"] = df.apply(
    lambda row: (
        pd.to_datetime(row["order_date"]) + pd.Timedelta(days=10)
    ).strftime("%Y-%m-%d")
    if pd.isna(row["delivery_date"]) and not pd.isna(row["order_date"])
    else row["delivery_date"],
    axis=1
)

print(f"\n✅ Step 7 — Nulls handled:")
print(f"   actual_unit_price filled: {null_actual}")
print(f"   order_type filled:        {null_order_type}")
print(f"   delivery_date filled:     {null_del}")

# ─────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────
final_rows  = len(df)
total_nulls = df.isnull().sum().sum()

print(f"\n{'='*45}")
print(f"📊 CLEANING SUMMARY — fact_purchase_orders")
print(f"{'='*45}")
print(f"  Original rows:     {original_rows}")
print(f"  Final rows:        {final_rows}")
print(f"  Rows removed:      {original_rows - final_rows}")
print(f"  Remaining nulls:   {total_nulls}")
print(f"{'='*45}")

# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
df.to_csv(f"{CLEANED_DIR}/fact_purchase_orders.csv", index=False)
print(f"\n🎉 Cleaned fact_purchase_orders.csv saved to: {CLEANED_DIR}")