import pandas as pd
import numpy as np
from datetime import date
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
OUTPUT_DIR = "../05_data/cleaned"
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(42)

# ─────────────────────────────────────────
# LOAD DIM TABLES
# ─────────────────────────────────────────
dim_product   = pd.read_csv(f"{OUTPUT_DIR}/dim_product.csv")
dim_warehouse = pd.read_csv(f"{OUTPUT_DIR}/dim_warehouse.csv")

# ─────────────────────────────────────────
# LEAKAGE PATTERN CONFIG (Day 5 design)
# ─────────────────────────────────────────

# Dead stock probability by product category
dead_stock_prob = {
    "Packaged Food":  0.35,  # Highest risk — expiry sensitive
    "Personal Care":  0.15,  # Medium risk — seasonal
    "Home Care":      0.05,  # Low risk — steady demand
}

# Holding cost multiplier by warehouse
# WH-04 Sylhet = stock piles up, higher effective holding
warehouse_stock_multiplier = {
    "WH-01": 1.0,   # Central, fast turnover
    "WH-02": 1.2,   # Moderate
    "WH-03": 1.4,   # Slow
    "WH-04": 1.7,   # Worst — rural, stock accumulates
}

# Monthly snapshot — Jan to Dec 2024
MONTHS = [
    ("2025-01-31", 1), ("2025-02-28", 2), ("2025-03-31", 3),
    ("2025-04-30", 4), ("2025-05-31", 5), ("2025-06-30", 6),
    ("2025-07-31", 7), ("2025-08-31", 8), ("2025-09-30", 9),
    ("2025-10-31", 10),("2025-11-30", 11),("2025-12-31", 12),
]

# ─────────────────────────────────────────
# GENERATE SNAPSHOTS
# ─────────────────────────────────────────
records = []
snapshot_counter = 1

for _, product in dim_product.iterrows():
    for _, warehouse in dim_warehouse.iterrows():

        dead_prob   = dead_stock_prob[product["category"]]
        wh_mult     = warehouse_stock_multiplier[warehouse["warehouse_id"]]
        is_dead     = np.random.random() < dead_prob
        hold_rate   = float(warehouse["monthly_holding_rate"])
        std_cost    = float(product["standard_cost"])
        max_stock   = int(product["max_stock_level"])

        # Stock age — if dead stock, age > 90 days
        if is_dead:
            stock_age = np.random.randint(91, 180)
        else:
            stock_age = np.random.randint(5, 89)

        prev_closing = np.random.randint(
            int(max_stock * 0.1 * wh_mult),
            int(max_stock * 0.4 * wh_mult)
        )

        for snapshot_date, month_num in MONTHS:
            snapshot_id  = f"INV-2024-{snapshot_counter:05d}"
            opening      = prev_closing
            closing      = max(0, opening + np.random.randint(-50, 100))
            avg_stock    = round((opening + closing) / 2, 0)
            avg_val      = round(avg_stock * std_cost * wh_mult, 2)
            holding_cost = round(avg_val * hold_rate, 2)

            # Seasonal spike — Apr-Jun procurement season
            if month_num in [4, 5, 6]:
                avg_val      = round(avg_val * np.random.uniform(1.1, 1.3), 2)
                holding_cost = round(avg_val * hold_rate, 2)

            records.append({
                "snapshot_id":    snapshot_id,
                "product_id":     product["product_id"],
                "date_id":        snapshot_date,
                "warehouse_id":   warehouse["warehouse_id"],
                "snapshot_date":  snapshot_date,
                "opening_stock":  opening,
                "closing_stock":  closing,
                "avg_stock_value":avg_val,
                "stock_age_days": stock_age,
                "is_dead_stock":  int(is_dead),
                "holding_cost":   holding_cost,
            })

            prev_closing     = closing
            snapshot_counter += 1

fact_inventory_snapshot = pd.DataFrame(records)

# ─────────────────────────────────────────
# QUICK SANITY CHECK
# ─────────────────────────────────────────
print("✅ fact_inventory_snapshot →", len(fact_inventory_snapshot), "rows")

print("\n📊 Dead stock by product category:")
dead = fact_inventory_snapshot[fact_inventory_snapshot["is_dead_stock"] == 1]
print(
    dead.merge(dim_product[["product_id","category"]], on="product_id")
    .groupby("category")["snapshot_id"].count()
    .sort_values(ascending=False)
)

print("\n📊 Total holding cost by warehouse:")
print(
    fact_inventory_snapshot.groupby("warehouse_id")["holding_cost"]
    .sum()
    .sort_values(ascending=False)
    .apply(lambda x: f"৳{x:,.0f}")
)

print("\n📊 Dead stock %:")
pct = len(dead) / len(fact_inventory_snapshot) * 100
print(f"  {pct:.1f}% of all snapshots flagged as dead stock")

# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
fact_inventory_snapshot.to_csv(
    f"{OUTPUT_DIR}/fact_inventory_snapshot.csv", index=False
)
print("\n🎉 fact_inventory_snapshot.csv saved to:", OUTPUT_DIR)