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

NUM_SHIPMENTS = 800  # 1 bochor, 6 route, ~133 shipments/route

# ─────────────────────────────────────────
# LOAD DIM TABLES
# ─────────────────────────────────────────
dim_route     = pd.read_csv(f"{OUTPUT_DIR}/dim_route.csv")
dim_warehouse = pd.read_csv(f"{OUTPUT_DIR}/dim_warehouse.csv")

# ─────────────────────────────────────────
# LEAKAGE PATTERN CONFIG (Day 5 design)
# ─────────────────────────────────────────

# Freight cost overrun % by route
route_overrun = {
    "RT-01": (-0.02, 0.05),   # Clean — Dhaka Metro
    "RT-02": (0.02, 0.08),    # Normal — Dhaka-Chattogram
    "RT-03": (0.02, 0.08),    # Normal — Chattogram Coastal
    "RT-04": (0.12, 0.20),    # Villain — Khulna-Jessore
    "RT-05": (0.20, 0.35),    # Worst villain — Sylhet Tea Belt
    "RT-06": (0.05, 0.15),    # Moderate — Dhaka-Sylhet Highway
}

# Late delivery probability by route
route_late_prob = {
    "RT-01": 0.06,   # 6% late
    "RT-02": 0.07,   # 7% late
    "RT-03": 0.08,   # 8% late
    "RT-04": 0.28,   # 28% late — villain
    "RT-05": 0.40,   # 40% late — worst villain
    "RT-06": 0.18,   # 18% late — moderate
}

# Actual distance overrun by route
route_distance_overrun = {
    "RT-01": (0.00, 0.05),
    "RT-02": (0.00, 0.05),
    "RT-03": (0.00, 0.05),
    "RT-04": (0.05, 0.15),
    "RT-05": (0.10, 0.25),
    "RT-06": (0.03, 0.10),
}

LATE_PENALTY = 500.0

# ─────────────────────────────────────────
# GENERATE SHIPMENTS
# ─────────────────────────────────────────
records = []

for i in range(1, NUM_SHIPMENTS + 1):
    shipment_id = f"SHP-2024-{i:04d}"
    route       = dim_route.sample(1).iloc[0]
    route_id    = route["route_id"]

    # Origin warehouse from route
    warehouse_id = route["origin_warehouse"]

    # Random shipment date in 2024
    shipment_date = date(2025, 1, 1) + timedelta(days=np.random.randint(0, 365))

    # Planned freight cost = planned_distance × cost_per_km
    planned_distance = float(route["planned_distance_km"])
    cost_per_km      = float(route["cost_per_km"])
    planned_cost     = round(planned_distance * cost_per_km, 2)

    # Actual distance = planned + overrun
    dist_min, dist_max   = route_distance_overrun[route_id]
    dist_overrun         = np.random.uniform(dist_min, dist_max)
    actual_distance      = round(planned_distance * (1 + dist_overrun), 2)

    # Actual freight cost = planned + cost overrun
    cost_min, cost_max = route_overrun[route_id]
    cost_overrun       = np.random.uniform(cost_min, cost_max)
    actual_cost        = round(planned_cost * (1 + cost_overrun), 2)

    # Seasonal spike — Apr-Jun and Oct-Dec
    month = shipment_date.month
    if month in [4, 5, 6, 10, 11, 12]:
        actual_cost = round(actual_cost * np.random.uniform(1.05, 1.15), 2)

    # Delivery status
    late_prob = route_late_prob[route_id]
    rand      = np.random.random()
    if rand < late_prob:
        delivery_status = "Late"
        late_penalty    = LATE_PENALTY
    elif rand < late_prob + 0.02:
        delivery_status = "Failed"
        late_penalty    = LATE_PENALTY * 2
    else:
        delivery_status = "On-Time"
        late_penalty    = 0.0

    records.append({
        "shipment_id":          shipment_id,
        "route_id":             route_id,
        "date_id":              shipment_date.strftime("%Y-%m-%d"),
        "shipment_date":        shipment_date.strftime("%Y-%m-%d"),
        "warehouse_id":         warehouse_id,
        "planned_freight_cost": planned_cost,
        "actual_freight_cost":  actual_cost,
        "planned_distance_km":  planned_distance,
        "actual_distance_km":   actual_distance,
        "delivery_status":      delivery_status,
        "late_penalty":         late_penalty,
    })

fact_shipments = pd.DataFrame(records)

# ─────────────────────────────────────────
# QUICK SANITY CHECK
# ─────────────────────────────────────────
fact_shipments["cost_overrun_pct"] = (
    (fact_shipments["actual_freight_cost"] - fact_shipments["planned_freight_cost"])
    / fact_shipments["planned_freight_cost"] * 100
).round(2)

print("✅ fact_shipments →", len(fact_shipments), "rows")

print("\n📊 Avg cost overrun % by route:")
print(
    fact_shipments.groupby("route_id")["cost_overrun_pct"]
    .mean()
    .sort_values(ascending=False)
    .round(2)
)

print("\n📊 Late/Failed delivery % by route:")
late = fact_shipments[fact_shipments["delivery_status"].isin(["Late", "Failed"])]
print(
    (late.groupby("route_id")["shipment_id"].count()
    / fact_shipments.groupby("route_id")["shipment_id"].count() * 100)
    .sort_values(ascending=False)
    .round(1)
)

print("\n📊 Total late penalty:")
print(f"  ৳{fact_shipments['late_penalty'].sum():,.0f}")

# ─────────────────────────────────────────
# EXPORT (drop sanity check column)
# ─────────────────────────────────────────
fact_shipments.drop(columns=["cost_overrun_pct"]).to_csv(
    f"{OUTPUT_DIR}/fact_shipments.csv", index=False
)
print("\n🎉 fact_shipments.csv saved to:", OUTPUT_DIR)