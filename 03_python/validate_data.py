import pandas as pd
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
CLEANED_DIR = "../05_data/cleaned"

# ─────────────────────────────────────────
# LOAD ALL CLEANED TABLES
# ─────────────────────────────────────────
print("📦 Loading all cleaned tables...")
dim_supplier   = pd.read_csv(f"{CLEANED_DIR}/dim_supplier.csv")
dim_product    = pd.read_csv(f"{CLEANED_DIR}/dim_product.csv")
dim_warehouse  = pd.read_csv(f"{CLEANED_DIR}/dim_warehouse.csv")
dim_route      = pd.read_csv(f"{CLEANED_DIR}/dim_route.csv")
dim_date       = pd.read_csv(f"{CLEANED_DIR}/dim_date.csv")
fact_po        = pd.read_csv(f"{CLEANED_DIR}/fact_purchase_orders.csv")
fact_inv       = pd.read_csv(f"{CLEANED_DIR}/fact_inventory_snapshot.csv")
fact_shp       = pd.read_csv(f"{CLEANED_DIR}/fact_shipments.csv")
fact_ful       = pd.read_csv(f"{CLEANED_DIR}/fact_order_fulfillment.csv")

all_passed = True

# ─────────────────────────────────────────
# CHECK 1: Row Counts
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 1: Row Counts")
print("="*50)

expected = {
    "dim_supplier":           15,
    "dim_product":            30,
    "dim_warehouse":           4,
    "dim_route":               6,
    "dim_date":              365,
    "fact_purchase_orders":  1200,
    "fact_inventory_snapshot":1440,
    "fact_shipments":         800,
    "fact_order_fulfillment":1062,
}

tables = {
    "dim_supplier":            dim_supplier,
    "dim_product":             dim_product,
    "dim_warehouse":           dim_warehouse,
    "dim_route":               dim_route,
    "dim_date":                dim_date,
    "fact_purchase_orders":    fact_po,
    "fact_inventory_snapshot": fact_inv,
    "fact_shipments":          fact_shp,
    "fact_order_fulfillment":  fact_ful,
}

for name, df in tables.items():
    exp = expected[name]
    act = len(df)
    status = "✅" if act == exp else "❌"
    if act != exp:
        all_passed = False
    print(f"  {status} {name}: {act} rows (expected {exp})")

# ─────────────────────────────────────────
# CHECK 2: Null Check
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 2: Null Values")
print("="*50)

for name, df in tables.items():
    # return_reason nullable by design — skip koro
    check_df = df.drop(columns=["return_reason"], errors="ignore")
    total_nulls = check_df.isnull().sum().sum()
    status = "✅" if total_nulls == 0 else "⚠️"
    if total_nulls > 0:
        null_cols = check_df.isnull().sum()
        null_cols = null_cols[null_cols > 0].to_dict()
        print(f"  {status} {name}: {total_nulls} nulls → {null_cols}")
        all_passed = False
    else:
        print(f"  {status} {name}: 0 nulls")

# ─────────────────────────────────────────
# CHECK 3: Duplicate Primary Keys
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 3: Duplicate Primary Keys")
print("="*50)

pk_map = {
    "dim_supplier":            ("dim_supplier",            "supplier_id"),
    "dim_product":             ("dim_product",             "product_id"),
    "dim_warehouse":           ("dim_warehouse",           "warehouse_id"),
    "dim_route":               ("dim_route",               "route_id"),
    "dim_date":                ("dim_date",                "date_id"),
    "fact_purchase_orders":    ("fact_purchase_orders",    "po_id"),
    "fact_inventory_snapshot": ("fact_inventory_snapshot", "snapshot_id"),
    "fact_shipments":          ("fact_shipments",          "shipment_id"),
    "fact_order_fulfillment":  ("fact_order_fulfillment",  "fulfillment_id"),
}

for name, (tbl_name, pk_col) in pk_map.items():
    df   = tables[name]
    dups = df[pk_col].duplicated().sum()
    status = "✅" if dups == 0 else "❌"
    if dups > 0:
        all_passed = False
    print(f"  {status} {name} [{pk_col}]: {dups} duplicates")

# ─────────────────────────────────────────
# CHECK 4: Referential Integrity
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 4: Referential Integrity")
print("="*50)

def check_fk(child_df, child_col, parent_df, parent_col, label):
    global all_passed
    valid   = set(parent_df[parent_col].astype(str))
    child   = child_df[child_col].astype(str)
    orphans = (~child.isin(valid)).sum()
    status  = "✅" if orphans == 0 else "❌"
    if orphans > 0:
        all_passed = False
    print(f"  {status} {label}: {orphans} orphan records")

check_fk(fact_po,  "supplier_id", dim_supplier,  "supplier_id", "fact_po → dim_supplier")
check_fk(fact_po,  "product_id",  dim_product,   "product_id",  "fact_po → dim_product")
check_fk(fact_inv, "product_id",  dim_product,   "product_id",  "fact_inv → dim_product")
check_fk(fact_inv, "warehouse_id",dim_warehouse, "warehouse_id","fact_inv → dim_warehouse")
check_fk(fact_shp, "route_id",    dim_route,     "route_id",    "fact_shp → dim_route")
check_fk(fact_shp, "warehouse_id",dim_warehouse, "warehouse_id","fact_shp → dim_warehouse")
check_fk(fact_ful, "warehouse_id",dim_warehouse, "warehouse_id","fact_ful → dim_warehouse")
check_fk(fact_ful, "po_id",       fact_po,       "po_id",       "fact_ful → fact_po")

# ─────────────────────────────────────────
# CHECK 5: ID Format Validation
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 5: ID Format Validation")
print("="*50)

def check_format(df, col, pattern, label):
    global all_passed
    invalid = (~df[col].astype(str).str.match(pattern)).sum()
    status  = "✅" if invalid == 0 else "❌"
    if invalid > 0:
        all_passed = False
    print(f"  {status} {label}: {invalid} invalid format")

check_format(fact_po,  "supplier_id", r"SUP-\d{3}", "fact_po.supplier_id")
check_format(fact_po,  "product_id",  r"PRD-\d{3}", "fact_po.product_id")
check_format(fact_inv, "product_id",  r"PRD-\d{3}", "fact_inv.product_id")
check_format(fact_inv, "warehouse_id",r"WH-\d{2}",  "fact_inv.warehouse_id")
check_format(fact_shp, "route_id",    r"RT-\d{2}",  "fact_shp.route_id")
check_format(fact_shp, "warehouse_id",r"WH-\d{2}",  "fact_shp.warehouse_id")
check_format(fact_ful, "warehouse_id",r"WH-\d{2}",  "fact_ful.warehouse_id")

# ─────────────────────────────────────────
# CHECK 6: Business Logic Validation
# ─────────────────────────────────────────
print("\n" + "="*50)
print("CHECK 6: Business Logic")
print("="*50)

# actual_unit_price should not be negative
neg_price = (fact_po["actual_unit_price"] < 0).sum()
print(f"  {'✅' if neg_price == 0 else '❌'} fact_po: negative actual_unit_price: {neg_price}")

# holding_cost should not be negative
neg_holding = (fact_inv["holding_cost"] < 0).sum()
print(f"  {'✅' if neg_holding == 0 else '❌'} fact_inv: negative holding_cost: {neg_holding}")

# actual_freight_cost should not be negative
neg_freight = (fact_shp["actual_freight_cost"] < 0).sum()
print(f"  {'✅' if neg_freight == 0 else '❌'} fact_shp: negative actual_freight_cost: {neg_freight}")

# late_penalty should not be negative
neg_penalty = (fact_shp["late_penalty"] < 0).sum()
print(f"  {'✅' if neg_penalty == 0 else '❌'} fact_shp: negative late_penalty: {neg_penalty}")

# return_cost should not be negative
neg_return = (fact_ful["return_cost"] < 0).sum()
print(f"  {'✅' if neg_return == 0 else '❌'} fact_ful: negative return_cost: {neg_return}")

# is_return=1 must have order_status=Returned
mismatch_r = ((fact_ful["is_return"]==1) & (fact_ful["order_status"]!="Returned")).sum()
print(f"  {'✅' if mismatch_r == 0 else '❌'} fact_ful: is_return/order_status mismatch: {mismatch_r}")

# is_partial=1 must have order_status=Partial
mismatch_p = ((fact_ful["is_partial"]==1) & (fact_ful["order_status"]!="Partial")).sum()
print(f"  {'✅' if mismatch_p == 0 else '❌'} fact_ful: is_partial/order_status mismatch: {mismatch_p}")

# stock_age_days >= 0
neg_age = (fact_inv["stock_age_days"] < 0).sum()
print(f"  {'✅' if neg_age == 0 else '❌'} fact_inv: negative stock_age_days: {neg_age}")

# ─────────────────────────────────────────
# FINAL VERDICT
# ─────────────────────────────────────────
print("\n" + "="*50)
if all_passed:
    print("🎉 ALL CHECKS PASSED — Data is clean and ready for SQL Server load!")
else:
    print("⚠️  SOME CHECKS FAILED — Review issues above before SQL load.")
print("="*50)