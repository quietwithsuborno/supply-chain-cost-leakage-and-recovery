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

RETURN_COST       = 300.0
PARTIAL_EXTRA     = 800.0

# ─────────────────────────────────────────
# LOAD DIM + FACT TABLES
# ─────────────────────────────────────────
dim_warehouse        = pd.read_csv(f"{OUTPUT_DIR}/dim_warehouse.csv")
fact_purchase_orders = pd.read_csv(f"{OUTPUT_DIR}/fact_purchase_orders.csv")

# Only completed POs get fulfillment records
completed_pos = fact_purchase_orders[
    fact_purchase_orders["po_status"] == "Completed"
].reset_index(drop=True)

print(f"📦 Completed POs to fulfill: {len(completed_pos)}")

# ─────────────────────────────────────────
# LEAKAGE PATTERN CONFIG (Day 5 design)
# ─────────────────────────────────────────

# Return rate by warehouse
warehouse_return_prob = {
    "WH-01": 0.02,   # Best — Dhaka Central, strong QC
    "WH-02": 0.05,   # Moderate
    "WH-03": 0.07,   # Below average
    "WH-04": 0.12,   # Worst — Sylhet, remote, weak QC
}

# Partial shipment rate by warehouse
warehouse_partial_prob = {
    "WH-01": 0.03,   # Best
    "WH-02": 0.07,   # Moderate
    "WH-03": 0.14,   # Worst — Khulna, stock inconsistency
    "WH-04": 0.09,   # Bad
}

# Return reasons pool
return_reasons = [
    "Damaged goods",
    "Wrong product delivered",
    "Quality issue",
    "Excess quantity sent",
    "Customer order cancellation",
    "Expired product",
]

# ─────────────────────────────────────────
# GENERATE FULFILLMENT RECORDS
# ─────────────────────────────────────────
records = []

for i, po in completed_pos.iterrows():
    fulfillment_id = f"FUL-2024-{i+1:04d}"

    # Assign warehouse randomly (weighted — Dhaka handles more)
    warehouse = np.random.choice(
        ["WH-01", "WH-02", "WH-03", "WH-04"],
        p=[0.45, 0.25, 0.18, 0.12]
    )

    # Fulfillment date = delivery_date + 1-3 days processing
    delivery_date    = pd.to_datetime(po["delivery_date"])
    fulfillment_date = delivery_date + timedelta(days=np.random.randint(1, 4))

    # Return logic
    return_prob = warehouse_return_prob[warehouse]
    is_return   = int(np.random.random() < return_prob)
    return_reason = (
        np.random.choice(return_reasons) if is_return else ""
    )
    return_cost = RETURN_COST if is_return else 0.0

    # Partial logic — cannot be both returned and partial
    partial_prob = warehouse_partial_prob[warehouse]
    is_partial   = int((not is_return) and (np.random.random() < partial_prob))
    partial_cost = PARTIAL_EXTRA if is_partial else 0.0

    # Order status
    if is_return:
        order_status = "Returned"
    elif is_partial:
        order_status = "Partial"
    else:
        order_status = "Complete"

    records.append({
        "fulfillment_id":    fulfillment_id,
        "po_id":             po["po_id"],
        "warehouse_id":      warehouse,
        "fulfillment_date":  fulfillment_date.strftime("%Y-%m-%d"),
        "date_id":           fulfillment_date.strftime("%Y-%m-%d"),
        "order_status":      order_status,
        "is_return":         is_return,
        "return_reason":     return_reason,
        "return_cost":       return_cost,
        "is_partial":        is_partial,
        "partial_extra_cost":partial_cost,
    })

fact_order_fulfillment = pd.DataFrame(records)

# ─────────────────────────────────────────
# QUICK SANITY CHECK
# ─────────────────────────────────────────
print("✅ fact_order_fulfillment →", len(fact_order_fulfillment), "rows")

print("\n📊 Order status distribution:")
print(fact_order_fulfillment["order_status"].value_counts())

print("\n📊 Return rate by warehouse:")
for wh in ["WH-01","WH-02","WH-03","WH-04"]:
    wh_df   = fact_order_fulfillment[fact_order_fulfillment["warehouse_id"] == wh]
    ret_pct = wh_df["is_return"].mean() * 100
    par_pct = wh_df["is_partial"].mean() * 100
    print(f"  {wh} → Return: {ret_pct:.1f}%  Partial: {par_pct:.1f}%")

print("\n📊 Total fulfillment leakage:")
total_return  = fact_order_fulfillment["return_cost"].sum()
total_partial = fact_order_fulfillment["partial_extra_cost"].sum()
print(f"  Return cost:  ৳{total_return:,.0f}")
print(f"  Partial cost: ৳{total_partial:,.0f}")
print(f"  Total:        ৳{total_return + total_partial:,.0f}")

# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
fact_order_fulfillment.to_csv(
    f"{OUTPUT_DIR}/fact_order_fulfillment.csv", index=False
)
print("\n🎉 fact_order_fulfillment.csv saved to:", OUTPUT_DIR)