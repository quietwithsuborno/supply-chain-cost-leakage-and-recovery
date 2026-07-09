import pandas as pd
import pyodbc
import os

# ─────────────────────────────────────────
# CONFIG — tomar SQL Server info diye update koro
# ─────────────────────────────────────────
SERVER   = "SUBORNO\\SQLEXPRESS"   
DATABASE = "BCPL_CostLeakage"
DRIVER   = "ODBC Driver 17 for SQL Server"

CLEANED_DIR = "../05_data/cleaned"

# ─────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────
conn_str = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

print("🔌 Connecting to SQL Server...")
conn   = pyodbc.connect(conn_str)
cursor = conn.cursor()
print("✅ Connected!\n")

# ─────────────────────────────────────────
# HELPER — chunk insert
# ─────────────────────────────────────────
def insert_table(csv_file, table_name, chunk_size=200):
    df = pd.read_csv(f"{CLEANED_DIR}/{csv_file}")

    # Explicitly convert all NaN/None to Python None
    df = df.astype(object).where(pd.notnull(df), None)

    cols         = ", ".join(df.columns)
    placeholders = ", ".join(["?" for _ in df.columns])
    sql          = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    total = 0
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        rows  = [tuple(row) for row in chunk.itertuples(index=False)]
        cursor.executemany(sql, rows)
        conn.commit()
        total += len(rows)

    print(f"  ✅ {table_name}: {total} rows inserted")
# ─────────────────────────────────────────
# INSERT ORDER — dim tables first, then fact
# (FK constraint order maintain korte hobe)
# ─────────────────────────────────────────
print("📦 Loading dimension tables...")
insert_table("dim_supplier.csv",  "dim_supplier")
insert_table("dim_product.csv",   "dim_product")
insert_table("dim_warehouse.csv", "dim_warehouse")
insert_table("dim_route.csv",     "dim_route")
insert_table("dim_date.csv",      "dim_date")

print("\n📦 Loading fact tables...")
insert_table("fact_purchase_orders.csv",    "fact_purchase_orders")
insert_table("fact_inventory_snapshot.csv", "fact_inventory_snapshot")
insert_table("fact_shipments.csv",          "fact_shipments")
insert_table("fact_order_fulfillment.csv",  "fact_order_fulfillment")

# ─────────────────────────────────────────
# VERIFY — row count check
# ─────────────────────────────────────────
print("\n📊 Row count verification:")
tables = [
    "dim_supplier", "dim_product", "dim_warehouse",
    "dim_route", "dim_date", "fact_purchase_orders",
    "fact_inventory_snapshot", "fact_shipments",
    "fact_order_fulfillment"
]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} rows")

cursor.close()
conn.close()
print("\n🎉 All data loaded successfully!")