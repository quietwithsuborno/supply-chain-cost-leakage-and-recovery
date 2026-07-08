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

# ─────────────────────────────────────────
# 1. dim_supplier (15 suppliers)
# ─────────────────────────────────────────
suppliers = [
    ("SUP-001", "Agropack Ltd.",           "Packaging",    "General",       "Gazipur",           "Local",  "2018-03-01", 7),
    ("SUP-002", "ChemSource BD",           "Raw Material", "Chemical",      "Narayanganj",       "Local",  "2017-06-15", 10),
    ("SUP-003", "GlobalPack Imports",      "Packaging",    "General",       "India",             "Import", "2019-01-10", 21),
    ("SUP-004", "NatureFresh Ingredients", "Raw Material", "Food",          "Bogura",            "Local",  "2016-09-01", 8),
    ("SUP-005", "SwiftBox Manufacturing",  "Packaging",    "General",       "Gazipur",           "Local",  "2020-02-20", 6),
    ("SUP-006", "PrimeChem Industries",    "Raw Material", "Chemical",      "Chattogram",        "Local",  "2015-11-05", 9),
    ("SUP-007", "EcoWrap Solutions",       "Packaging",    "General",       "Dhaka",             "Local",  "2021-04-12", 5),
    ("SUP-008", "AsiaFood Commodities",    "Raw Material", "Food",          "Thailand",          "Import", "2018-07-30", 25),
    ("SUP-009", "BioBase Materials",       "Raw Material", "Personal Care", "Narayanganj",       "Local",  "2019-03-18", 11),
    ("SUP-010", "FastPack Ltd.",           "Packaging",    "General",       "Gazipur",           "Local",  "2022-01-05", 5),
    ("SUP-011", "MegaChem Corp",           "Raw Material", "Chemical",      "China",             "Import", "2017-08-22", 30),
    ("SUP-012", "DeltaFood Supply",        "Raw Material", "Food",          "Mymensingh",        "Local",  "2016-05-14", 7),
    ("SUP-013", "GreenLeaf Extracts",      "Raw Material", "Personal Care", "Sylhet",            "Local",  "2020-10-09", 12),
    ("SUP-014", "PolyPack Industries",     "Packaging",    "General",       "Narayanganj",       "Local",  "2018-12-01", 6),
    ("SUP-015", "OrientChem Ltd.",         "Raw Material", "Chemical",      "China",             "Import", "2019-06-17", 28),
]

dim_supplier = pd.DataFrame(suppliers, columns=[
    "supplier_id", "supplier_name", "category", "sub_category",
    "location", "supplier_type", "contract_start", "standard_lead_days"
])

# ─────────────────────────────────────────
# 2. dim_product (30 SKUs)
# ─────────────────────────────────────────
products = [
    # Personal Care (PRD-001 to PRD-010)
    ("PRD-001", "Fresh Glow Soap 100g",         "Personal Care", "Piece",  45.00,  500, 5000),
    ("PRD-002", "ShineHair Shampoo 200ml",       "Personal Care", "Piece",  120.00, 300, 3000),
    ("PRD-003", "SoftSkin Face Wash 100ml",      "Personal Care", "Piece",  95.00,  250, 2500),
    ("PRD-004", "CoolMint Toothpaste 150g",      "Personal Care", "Piece",  65.00,  400, 4000),
    ("PRD-005", "DermaShield Lotion 250ml",      "Personal Care", "Piece",  180.00, 200, 2000),
    ("PRD-006", "AquaPure Hand Wash 500ml",      "Personal Care", "Piece",  110.00, 350, 3500),
    ("PRD-007", "NaturBloom Conditioner 200ml",  "Personal Care", "Piece",  135.00, 200, 2000),
    ("PRD-008", "SilkTouch Body Lotion 400ml",   "Personal Care", "Piece",  210.00, 150, 1500),
    ("PRD-009", "HerbalGlow Scrub 150g",         "Personal Care", "Piece",  155.00, 150, 1500),
    ("PRD-010", "FreshBreeze Deodorant 150ml",   "Personal Care", "Piece",  130.00, 250, 2500),
    # Home Care (PRD-011 to PRD-020)
    ("PRD-011", "BrightWash Detergent 1kg",      "Home Care",     "KG",     85.00,  600, 6000),
    ("PRD-012", "SparkleClean Dish Wash 500ml",  "Home Care",     "Piece",  55.00,  500, 5000),
    ("PRD-013", "FloorShine Cleaner 1L",         "Home Care",     "Litre",  75.00,  400, 4000),
    ("PRD-014", "FreshHome Toilet Cleaner 500ml","Home Care",     "Piece",  60.00,  350, 3500),
    ("PRD-015", "PowerWash Detergent 2kg",       "Home Care",     "KG",     155.00, 400, 4000),
    ("PRD-016", "GlassGuard Window Cleaner 1L",  "Home Care",     "Litre",  90.00,  300, 3000),
    ("PRD-017", "FabricSoft Fabric Softener 1L", "Home Care",     "Litre",  105.00, 250, 2500),
    ("PRD-018", "BugAway Insect Spray 500ml",    "Home Care",     "Piece",  120.00, 200, 2000),
    ("PRD-019", "DrainClear Pipe Cleaner 500ml", "Home Care",     "Piece",  80.00,  200, 2000),
    ("PRD-020", "AirFresh Room Freshener 300ml", "Home Care",     "Piece",  95.00,  300, 3000),
    # Packaged Food (PRD-021 to PRD-030)
    ("PRD-021", "CrunchBite Biscuit 200g",       "Packaged Food", "Piece",  35.00,  800, 8000),
    ("PRD-022", "SpiceMix Chanachur 150g",       "Packaged Food", "Piece",  30.00,  700, 7000),
    ("PRD-023", "QuickNoodle Instant 75g",       "Packaged Food", "Piece",  25.00,  1000,10000),
    ("PRD-024", "SweetMoment Cookie 150g",       "Packaged Food", "Piece",  40.00,  600, 6000),
    ("PRD-025", "CrispSnack Chips 100g",         "Packaged Food", "Piece",  28.00,  700, 7000),
    ("PRD-026", "MunchTime Crackers 200g",       "Packaged Food", "Piece",  38.00,  500, 5000),
    ("PRD-027", "NutriBar Energy Bar 50g",       "Packaged Food", "Piece",  55.00,  400, 4000),
    ("PRD-028", "FruitJam Strawberry 250g",      "Packaged Food", "Piece",  95.00,  300, 3000),
    ("PRD-029", "HoneyDrip Natural Honey 500g",  "Packaged Food", "Piece",  220.00, 200, 2000),
    ("PRD-030", "RoastedNut Mixed Nuts 200g",    "Packaged Food", "Piece",  185.00, 250, 2500),
]

dim_product = pd.DataFrame(products, columns=[
    "product_id", "product_name", "category", "unit_of_measure",
    "standard_cost", "reorder_level", "max_stock_level"
])

# ─────────────────────────────────────────
# 3. dim_warehouse (4 warehouses)
# ─────────────────────────────────────────
warehouses = [
    ("WH-01", "Tejgaon Central Warehouse", "Tejgaon, Dhaka", "Central",  50000, 0.0200),
    ("WH-02", "Chattogram Regional Hub",   "Chattogram",     "Regional", 25000, 0.0200),
    ("WH-03", "Khulna Distribution Center","Khulna",         "Regional", 18000, 0.0200),
    ("WH-04", "Sylhet Regional Depot",     "Sylhet",         "Regional", 15000, 0.0200),
]

dim_warehouse = pd.DataFrame(warehouses, columns=[
    "warehouse_id", "warehouse_name", "location", "type",
    "capacity_units", "monthly_holding_rate"
])

# ─────────────────────────────────────────
# 4. dim_route (6 routes)
# ─────────────────────────────────────────
routes = [
    ("RT-01", "Dhaka Metro",             "WH-01", "Dhaka City Distributors",      "Urban",      25.0,  12.0),
    ("RT-02", "Dhaka–Chattogram Highway","WH-01", "WH-02 / Chattogram Depot",     "Inter-city", 245.0, 12.0),
    ("RT-03", "Chattogram Coastal",      "WH-02", "Chattogram District Dealers",  "Urban",      40.0,  12.0),
    ("RT-04", "Khulna–Jessore Belt",     "WH-03", "Khulna/Jessore Distributors",  "Semi-urban", 80.0,  12.0),
    ("RT-05", "Sylhet Tea Belt",         "WH-04", "Sylhet District Dealers",      "Rural",      95.0,  12.0),
    ("RT-06", "Dhaka–Sylhet Highway",    "WH-01", "WH-04 / Sylhet Depot",         "Inter-city", 310.0, 12.0),
]

dim_route = pd.DataFrame(routes, columns=[
    "route_id", "route_name", "origin_warehouse", "destination",
    "route_type", "planned_distance_km", "cost_per_km"
])

# ─────────────────────────────────────────
# 5. dim_date (Jan 2024 – Dec 2024)
# ─────────────────────────────────────────
date_range = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")

dim_date = pd.DataFrame({
    "date_id":     date_range.strftime("%Y-%m-%d"),
    "day":         date_range.day,
    "month":       date_range.month,
    "month_name":  date_range.strftime("%B"),
    "quarter":     date_range.quarter,
    "year":        date_range.year,
    "day_of_week": date_range.strftime("%A"),
    "is_weekend":  (date_range.dayofweek >= 5).astype(int),
})

# ─────────────────────────────────────────
# EXPORT TO CSV
# ─────────────────────────────────────────
dim_supplier.to_csv(f"{OUTPUT_DIR}/dim_supplier.csv", index=False)
dim_product.to_csv(f"{OUTPUT_DIR}/dim_product.csv", index=False)
dim_warehouse.to_csv(f"{OUTPUT_DIR}/dim_warehouse.csv", index=False)
dim_route.to_csv(f"{OUTPUT_DIR}/dim_route.csv", index=False)
dim_date.to_csv(f"{OUTPUT_DIR}/dim_date.csv", index=False)

print("✅ dim_supplier   →", len(dim_supplier), "rows")
print("✅ dim_product    →", len(dim_product), "rows")
print("✅ dim_warehouse  →", len(dim_warehouse), "rows")
print("✅ dim_route      →", len(dim_route), "rows")
print("✅ dim_date       →", len(dim_date), "rows")
print("\n🎉 All dimension CSVs saved to:", OUTPUT_DIR)