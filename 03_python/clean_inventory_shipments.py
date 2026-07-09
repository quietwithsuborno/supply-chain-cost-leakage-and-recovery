import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
RAW_DIR     = "../05_data/raw"
CLEANED_DIR = "../05_data/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def fix_id(val, prefix, digits):
    """Standardize ID format — e.g. PRD001 / prd-001 → PRD-001"""
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "").replace("-", "")
    if val.startswith(prefix) and len(val) == len(prefix) + digits:
        return f"{prefix}-{val[len(prefix):]}"
    return val

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

def clean_text(val):
    if pd.isna(val):
        return val
    return str(val).strip().title()

# ═══════════════════════════════════════════
# PART A: fact_inventory_snapshot
# ═══════════════════════════════════════════
print("=" * 50)
print("PART A: fact_inventory_snapshot")
print("=" * 50)

inv = pd.read_csv(f"{RAW_DIR}/raw_inventory_snapshot.csv")
original_rows = len(inv)
print(f"📦 Loaded raw_inventory_snapshot: {original_rows} rows")

# Step 1: Remove duplicates
before = len(inv)
inv = inv.drop_duplicates(subset=["snapshot_id"], keep="first")
print(f"\n✅ Step 1 — Duplicates removed: {before - len(inv)}")

# Step 2: Standardize ID formats
inv["product_id"]   = inv["product_id"].apply(lambda x: fix_id(x, "PRD", 3))
inv["warehouse_id"] = inv["warehouse_id"].apply(lambda x: str(x).strip().upper().replace(" ", "") if not pd.isna(x) else x)

# Fix warehouse_id format — WH01 / wh-01 → WH-01
def fix_warehouse_id(val):
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "").replace("-", "")
    if val.startswith("WH") and len(val) == 4:
        return f"WH-{val[2:]}"
    return val

inv["warehouse_id"] = inv["warehouse_id"].apply(fix_warehouse_id)

prd_valid = inv["product_id"].str.match(r"PRD-\d{3}").sum()
wh_valid  = inv["warehouse_id"].str.match(r"WH-\d{2}").sum()
print(f"\n✅ Step 2 — ID format standardized:")
print(f"   product_id   valid: {prd_valid}/{len(inv)}")
print(f"   warehouse_id valid: {wh_valid}/{len(inv)}")

# Step 3: Standardize date formats
inv["snapshot_date"] = inv["snapshot_date"].apply(parse_date)
inv["date_id"]       = inv["date_id"].apply(parse_date)
print(f"\n✅ Step 3 — Date format standardized:")
print(f"   snapshot_date nulls: {inv['snapshot_date'].isna().sum()}")

# Step 4: Fix negative values
neg_holding = (inv["holding_cost"] < 0).sum()
inv.loc[inv["holding_cost"] < 0, "holding_cost"] = inv["holding_cost"].abs()
print(f"\n✅ Step 4 — Negative holding_cost fixed: {neg_holding}")

# Step 5: Fix outliers in closing_stock
outlier_stock = (inv["closing_stock"] > 50000).sum()
median_stock  = inv.loc[inv["closing_stock"] <= 50000, "closing_stock"].median()
inv.loc[inv["closing_stock"] > 50000, "closing_stock"] = int(median_stock)
print(f"\n✅ Step 5 — Outlier closing_stock fixed: {outlier_stock} (median: {int(median_stock)})")

# Step 6: Handle nulls
null_avg   = inv["avg_stock_value"].isna().sum()
null_age   = inv["stock_age_days"].isna().sum()
null_hold  = inv["holding_cost"].isna().sum()

# avg_stock_value null → fill with median per product
inv["avg_stock_value"] = inv.groupby("product_id")["avg_stock_value"].transform(
    lambda x: x.fillna(x.median())
)

# stock_age_days null → fill with median
median_age = inv["stock_age_days"].median()
inv["stock_age_days"] = inv["stock_age_days"].fillna(median_age)

# holding_cost null → recalculate from avg_stock_value × 0.02
inv["holding_cost"] = inv.apply(
    lambda row: round(row["avg_stock_value"] * 0.02, 2)
    if pd.isna(row["holding_cost"]) else row["holding_cost"],
    axis=1
)

print(f"\n✅ Step 6 — Nulls handled:")
print(f"   avg_stock_value filled: {null_avg}")
print(f"   stock_age_days filled:  {null_age}")
print(f"   holding_cost filled:    {null_hold}")

# Final summary
print(f"\n{'='*45}")
print(f"📊 CLEANING SUMMARY — fact_inventory_snapshot")
print(f"{'='*45}")
print(f"  Original rows:   {original_rows}")
print(f"  Final rows:      {len(inv)}")
print(f"  Rows removed:    {original_rows - len(inv)}")
print(f"  Remaining nulls: {inv.isnull().sum().sum()}")
print(f"{'='*45}")

inv.to_csv(f"{CLEANED_DIR}/fact_inventory_snapshot.csv", index=False)
print(f"🎉 Cleaned fact_inventory_snapshot.csv saved!\n")


# ═══════════════════════════════════════════
# PART B: fact_shipments
# ═══════════════════════════════════════════
print("=" * 50)
print("PART B: fact_shipments")
print("=" * 50)

shp = pd.read_csv(f"{RAW_DIR}/raw_shipments.csv")
original_rows_shp = len(shp)
print(f"📦 Loaded raw_shipments: {original_rows_shp} rows")

# Step 1: Remove duplicates
before = len(shp)
shp = shp.drop_duplicates(subset=["shipment_id"], keep="first")
print(f"\n✅ Step 1 — Duplicates removed: {before - len(shp)}")

# Step 2: Standardize ID formats
def fix_route_id(val):
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "").replace("-", "")
    if val.startswith("RT") and len(val) == 4:
        return f"RT-{val[2:]}"
    return val

shp["route_id"]     = shp["route_id"].apply(fix_route_id)
shp["warehouse_id"] = shp["warehouse_id"].apply(fix_warehouse_id)

rt_valid = shp["route_id"].str.match(r"RT-\d{2}").sum()
wh_valid = shp["warehouse_id"].str.match(r"WH-\d{2}").sum()
print(f"\n✅ Step 2 — ID format standardized:")
print(f"   route_id     valid: {rt_valid}/{len(shp)}")
print(f"   warehouse_id valid: {wh_valid}/{len(shp)}")

# Step 3: Standardize date formats
shp["shipment_date"] = shp["shipment_date"].apply(parse_date)
shp["date_id"]       = shp["date_id"].apply(parse_date)
print(f"\n✅ Step 3 — Date format standardized:")
print(f"   shipment_date nulls: {shp['shipment_date'].isna().sum()}")

# Step 4: Clean delivery_status
shp["delivery_status"] = shp["delivery_status"].apply(clean_text)
valid_statuses         = ["On-Time", "Late", "Failed"]

# Fix "On-Time" — title() makes it "On-Time" correctly
shp["delivery_status"] = shp["delivery_status"].replace({
    "On-Time": "On-Time",
    "Late":    "Late",
    "Failed":  "Failed"
})

null_status = shp["delivery_status"].isna().sum()
shp["delivery_status"] = shp["delivery_status"].fillna("On-Time")
print(f"\n✅ Step 4 — delivery_status cleaned, nulls filled: {null_status}")

# Step 5: Fix negative late_penalty
neg_penalty = (shp["late_penalty"] < 0).sum()
shp.loc[shp["late_penalty"] < 0, "late_penalty"] = shp["late_penalty"].abs()
print(f"\n✅ Step 5 — Negative late_penalty fixed: {neg_penalty}")

# Step 6: Fix outliers in actual_freight_cost
outlier_freight = (shp["actual_freight_cost"] > 20000).sum()
median_freight  = shp.loc[shp["actual_freight_cost"] <= 20000, "actual_freight_cost"].median()
shp.loc[shp["actual_freight_cost"] > 20000, "actual_freight_cost"] = round(median_freight, 2)
print(f"\n✅ Step 6 — Outlier actual_freight_cost fixed: {outlier_freight} (median: ৳{median_freight:,.0f})")

# Step 7: Handle nulls
null_freight  = shp["actual_freight_cost"].isna().sum()
null_distance = shp["actual_distance_km"].isna().sum()

shp["actual_freight_cost"] = shp.groupby("route_id")["actual_freight_cost"].transform(
    lambda x: x.fillna(x.median())
)
shp["actual_distance_km"] = shp.groupby("route_id")["actual_distance_km"].transform(
    lambda x: x.fillna(x.median())
)

print(f"\n✅ Step 7 — Nulls handled:")
print(f"   actual_freight_cost filled: {null_freight}")
print(f"   actual_distance_km filled:  {null_distance}")

# Final summary
print(f"\n{'='*45}")
print(f"📊 CLEANING SUMMARY — fact_shipments")
print(f"{'='*45}")
print(f"  Original rows:   {original_rows_shp}")
print(f"  Final rows:      {len(shp)}")
print(f"  Rows removed:    {original_rows_shp - len(shp)}")
print(f"  Remaining nulls: {shp.isnull().sum().sum()}")
print(f"{'='*45}")

shp.to_csv(f"{CLEANED_DIR}/fact_shipments.csv", index=False)
print(f"🎉 Cleaned fact_shipments.csv saved!")