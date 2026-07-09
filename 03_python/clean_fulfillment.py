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
def fix_warehouse_id(val):
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "").replace("-", "")
    if val.startswith("WH") and len(val) == 4:
        return f"WH-{val[2:]}"
    return val

def fix_po_id(val):
    """PO20240001 / po-2024-0001 → PO-2024-0001"""
    if pd.isna(val):
        return val
    val = str(val).strip().upper().replace(" ", "")
    # Already correct format
    if val.startswith("PO-") and len(val) == 12:
        return val
    # Remove all dashes and reformat
    val = val.replace("-", "")
    if val.startswith("PO") and len(val) == 10:
        return f"PO-{val[2:6]}-{val[6:]}"
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

# ─────────────────────────────────────────
# LOAD MESSY DATA
# ─────────────────────────────────────────
ful = pd.read_csv(f"{RAW_DIR}/raw_order_fulfillment.csv")
original_rows = len(ful)
print(f"📦 Loaded raw_order_fulfillment: {original_rows} rows")

# ─────────────────────────────────────────
# STEP 1: Remove Duplicates
# ─────────────────────────────────────────
before = len(ful)
ful = ful.drop_duplicates(subset=["fulfillment_id"], keep="first")
print(f"\n✅ Step 1 — Duplicates removed: {before - len(ful)}")

# ─────────────────────────────────────────
# STEP 2: Standardize ID Formats
# ─────────────────────────────────────────
ful["warehouse_id"] = ful["warehouse_id"].apply(fix_warehouse_id)
ful["po_id"]        = ful["po_id"].apply(fix_po_id)

wh_valid = ful["warehouse_id"].str.match(r"WH-\d{2}").sum()
po_valid = ful["po_id"].str.match(r"PO-\d{4}-\d{4}").sum()
print(f"\n✅ Step 2 — ID format standardized:")
print(f"   warehouse_id valid: {wh_valid}/{len(ful)}")
print(f"   po_id        valid: {po_valid}/{len(ful)}")

# ─────────────────────────────────────────
# STEP 3: Standardize Date Formats
# ─────────────────────────────────────────
ful["fulfillment_date"] = ful["fulfillment_date"].apply(parse_date)
ful["date_id"]          = ful["date_id"].apply(parse_date)

null_date = ful["fulfillment_date"].isna().sum()
print(f"\n✅ Step 3 — Date format standardized:")
print(f"   fulfillment_date nulls remaining: {null_date}")

# ─────────────────────────────────────────
# STEP 4: Fill null fulfillment_date
# → Use date_id as fallback
# ─────────────────────────────────────────
filled_date = 0
for idx, row in ful[ful["fulfillment_date"].isna()].iterrows():
    if not pd.isna(row["date_id"]):
        ful.loc[idx, "fulfillment_date"] = row["date_id"]
        filled_date += 1

print(f"\n✅ Step 4 — fulfillment_date nulls filled from date_id: {filled_date}")

# ─────────────────────────────────────────
# STEP 5: Clean Text Columns
# order_status → strip whitespace + Title Case
# ─────────────────────────────────────────
ful["order_status"] = ful["order_status"].apply(clean_text)

valid_statuses     = ["Complete", "Partial", "Returned"]
invalid_status     = (~ful["order_status"].isin(valid_statuses) & ful["order_status"].notna()).sum()
null_status        = ful["order_status"].isna().sum()
ful["order_status"] = ful["order_status"].fillna("Complete")

print(f"\n✅ Step 5 — order_status cleaned:")
print(f"   Invalid values: {invalid_status}")
print(f"   Nulls filled:   {null_status}")

# ─────────────────────────────────────────
# STEP 6: Fix Negative return_cost
# ─────────────────────────────────────────
neg_return = (ful["return_cost"] < 0).sum()
ful.loc[ful["return_cost"] < 0, "return_cost"] = ful["return_cost"].abs()
print(f"\n✅ Step 6 — Negative return_cost fixed: {neg_return}")

# ─────────────────────────────────────────
# STEP 7: Handle null partial_extra_cost
# If is_partial = 1 and partial_extra_cost null → fill 800
# If is_partial = 0 → fill 0
# ─────────────────────────────────────────
null_partial = ful["partial_extra_cost"].isna().sum()
ful["partial_extra_cost"] = ful.apply(
    lambda row: 800.0 if pd.isna(row["partial_extra_cost"]) and row["is_partial"] == 1
    else (0.0 if pd.isna(row["partial_extra_cost"]) else row["partial_extra_cost"]),
    axis=1
)
print(f"\n✅ Step 7 — null partial_extra_cost filled: {null_partial}")

# ─────────────────────────────────────────
# STEP 8: Fix return_reason nulls
# Non-returned orders → "N/A"
# Returned orders with null reason → "Unspecified"
# ─────────────────────────────────────────
null_reason = ful["return_reason"].isna().sum()
ful["return_reason"] = ful.apply(
    lambda row: "Unspecified" if pd.isna(row["return_reason"]) and row["is_return"] == 1
    else ("N/A" if pd.isna(row["return_reason"]) else row["return_reason"]),
    axis=1
)
print(f"\n✅ Step 8 — return_reason nulls handled: {null_reason}")

# ─────────────────────────────────────────
# STEP 9: Consistency Check
# is_return=1 → order_status must be "Returned"
# is_partial=1 → order_status must be "Partial"
# ─────────────────────────────────────────
mismatch_return  = ((ful["is_return"] == 1) & (ful["order_status"] != "Returned")).sum()
mismatch_partial = ((ful["is_partial"] == 1) & (ful["order_status"] != "Partial")).sum()

ful.loc[ful["is_return"] == 1,  "order_status"] = "Returned"
ful.loc[ful["is_partial"] == 1, "order_status"] = "Partial"

print(f"\n✅ Step 9 — Consistency fixes:")
print(f"   is_return/order_status mismatch fixed:  {mismatch_return}")
print(f"   is_partial/order_status mismatch fixed: {mismatch_partial}")

# ─────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────
final_rows  = len(ful)
total_nulls = ful.isnull().sum().sum()

print(f"\n{'='*45}")
print(f"📊 CLEANING SUMMARY — fact_order_fulfillment")
print(f"{'='*45}")
print(f"  Original rows:     {original_rows}")
print(f"  Final rows:        {final_rows}")
print(f"  Rows removed:      {original_rows - final_rows}")
print(f"  Remaining nulls:   {total_nulls}")
print(f"{'='*45}")

# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
ful.to_csv(f"{CLEANED_DIR}/fact_order_fulfillment.csv", index=False)
print(f"\n🎉 Cleaned fact_order_fulfillment.csv saved to: {CLEANED_DIR}")