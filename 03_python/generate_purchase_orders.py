import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
OUTPUT_DIR = "../05_data/cleaned"
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(42)

NUM_ORDERS = 1200  # 1 bochor, 15 supplier, ~80 orders/supplier

# ─────────────────────────────────────────
# LOAD DIM TABLES
# ─────────────────────────────────────────
dim_supplier = pd.read_csv(f"{OUTPUT_DIR}/dim_supplier.csv")
dim_product  = pd.read_csv(f"{OUTPUT_DIR}/dim_product.csv")

# ─────────────────────────────────────────
# LEAKAGE PATTERN CONFIG (Day 5 design)
# ─────────────────────────────────────────

# Procurement price variance by supplier
supplier_variance = {
    "SUP-001": (0.00, 0.02),   # Clean
    "SUP-002": (-0.02, 0.04),  # Normal
    "SUP-003": (0.12, 0.18),   # Villain — import, consistently overcharges
    "SUP-004": (-0.02, 0.04),  # Normal
    "SUP-005": (-0.01, 0.03),  # Normal
    "SUP-006": (-0.02, 0.04),  # Normal
    "SUP-007": (-0.01, 0.03),  # Normal
    "SUP-008": (0.07, 0.12),   # Villain — import food, moderate overcharge
    "SUP-009": (-0.02, 0.04),  # Normal
    "SUP-010": (-0.01, 0.03),  # Normal
    "SUP-011": (0.15, 0.22),   # Worst villain — China import
    "SUP-012": (-0.02, 0.04),  # Normal
    "SUP-013": (-0.01, 0.03),  # Normal
    "SUP-014": (-0.02, 0.04),  # Normal
    "SUP-015": (0.05, 0.10),   # Villain — rush orders only (handled below)
}

# Order type weights — 15% rush/emergency
ORDER_TYPES        = ["Regular", "Rush", "Emergency"]
ORDER_TYPE_WEIGHTS = [0.85, 0.10, 0.05]

# Rush/emergency premium (on top of supplier variance)
RUSH_PREMIUM = {
    "Regular":   (0.00, 0.00),
    "Rush":      (0.10, 0.15),
    "Emergency": (0.15, 0.20),
}

# ─────────────────────────────────────────
# GENERATE ORDERS
# ─────────────────────────────────────────
records = []

for i in range(1, NUM_ORDERS + 1):
    po_id      = f"PO-2024-{i:04d}"
    supplier   = dim_supplier.sample(1).iloc[0]
    product    = dim_product.sample(1).iloc[0]
    order_type = np.random.choice(ORDER_TYPES, p=ORDER_TYPE_WEIGHTS)

    # Random order date in 2024
    order_date = date(2024, 1, 1) + timedelta(days=np.random.randint(0, 366))

    # Delivery date = order date + lead days + some noise
    lead_days     = int(supplier["standard_lead_days"])
    delivery_date = order_date + timedelta(days=lead_days + np.random.randint(-2, 5))

    # Quantity
    quantity = np.random.randint(50, 500)

    # Standard price from dim_product
    standard_price = float(product["standard_cost"])

    # Actual price = standard + supplier variance + rush premium
    sup_var_min, sup_var_max = supplier_variance[supplier["supplier_id"]]
    rush_min, rush_max       = RUSH_PREMIUM[order_type]

    # SUP-015 villain only on rush/emergency
    if supplier["supplier_id"] == "SUP-015" and order_type == "Regular":
        sup_var_min, sup_var_max = -0.02, 0.04

    variance      = np.random.uniform(sup_var_min, sup_var_max)
    rush_premium  = np.random.uniform(rush_min, rush_max)
    actual_price  = round(standard_price * (1 + variance + rush_premium), 2)

    # PO status
    po_status = np.random.choice(
        ["Completed", "Pending", "Cancelled"],
        p=[0.88, 0.08, 0.04]
    )

    records.append({
        "po_id":               po_id,
        "supplier_id":         supplier["supplier_id"],
        "product_id":          product["product_id"],
        "order_date":          order_date.strftime("%Y-%m-%d"),
        "date_id":             order_date.strftime("%Y-%m-%d"),
        "quantity_ordered":    quantity,
        "standard_unit_price": standard_price,
        "actual_unit_price":   actual_price,
        "order_type":          order_type,
        "delivery_date":       delivery_date.strftime("%Y-%m-%d"),
        "po_status":           po_status,
    })

fact_purchase_orders = pd.DataFrame(records)

# ─────────────────────────────────────────
# QUICK SANITY CHECK
# ─────────────────────────────────────────
fact_purchase_orders["price_variance_pct"] = (
    (fact_purchase_orders["actual_unit_price"] - fact_purchase_orders["standard_unit_price"])
    / fact_purchase_orders["standard_unit_price"] * 100
).round(2)

print("✅ fact_purchase_orders →", len(fact_purchase_orders), "rows")
print("\n📊 Avg price variance % by supplier (top offenders):")
print(
    fact_purchase_orders.groupby("supplier_id")["price_variance_pct"]
    .mean()
    .sort_values(ascending=False)
    .head(6)
    .round(2)
)
print("\n📊 Order type distribution:")
print(fact_purchase_orders["order_type"].value_counts())

# ─────────────────────────────────────────
# EXPORT (drop sanity check column)
# ─────────────────────────────────────────
fact_purchase_orders.drop(columns=["price_variance_pct"]).to_csv(
    f"{OUTPUT_DIR}/fact_purchase_orders.csv", index=False
)
print("\n🎉 fact_purchase_orders.csv saved to:", OUTPUT_DIR)