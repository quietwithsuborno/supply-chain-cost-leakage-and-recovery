import subprocess
import sys
import os
from datetime import datetime

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
PYTHON = sys.executable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name, description):
    print(f"\n{'='*55}")
    print(f"▶  {description}")
    print(f"{'='*55}")
    script_path = os.path.join(SCRIPT_DIR, script_name)
    result = subprocess.run(
        [PYTHON, script_path],
        capture_output=False,
        text=True
    )
    if result.returncode != 0:
        print(f"\n❌ FAILED: {script_name} — pipeline stopped.")
        sys.exit(1)
    print(f"\n✅ DONE: {script_name}")

# ─────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────
start_time = datetime.now()

print("╔══════════════════════════════════════════════════════╗")
print("║   BCPL Cost Leakage Diagnostic — Data Pipeline      ║")
print("║   Bongo Consumer Products Ltd.                       ║")
print("╚══════════════════════════════════════════════════════╝")
print(f"\n🕐 Pipeline started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ── PHASE 1: Generate Clean Dimension + Fact Data ──
run_script("generate_dimensions.py",       "STEP 1/7 — Generate Dimension Tables")
run_script("generate_purchase_orders.py",  "STEP 2/7 — Generate Purchase Orders")
run_script("generate_inventory_snapshot.py","STEP 3/7 — Generate Inventory Snapshots")
run_script("generate_shipments.py",        "STEP 4/7 — Generate Shipments")
run_script("generate_order_fulfillment.py","STEP 5/7 — Generate Order Fulfillment")

# ── PHASE 2: Inject Messiness ──
run_script("inject_messiness.py",          "STEP 6/7 — Inject Messiness into Raw Data")

# ── PHASE 3: Clean ──
run_script("clean_purchase_orders.py",     "STEP 7a/7 — Clean Purchase Orders")
run_script("clean_inventory_shipments.py", "STEP 7b/7 — Clean Inventory & Shipments")
run_script("clean_fulfillment.py",         "STEP 7c/7 — Clean Order Fulfillment")

# ── PHASE 4: Validate ──
run_script("validate_data.py",             "STEP 8/7 — Validate All Cleaned Data")

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
end_time  = datetime.now()
duration  = (end_time - start_time).seconds

print("\n╔══════════════════════════════════════════════════════╗")
print("║   🎉 PIPELINE COMPLETE                               ║")
print("╠══════════════════════════════════════════════════════╣")
print(f"║   Started:  {start_time.strftime('%H:%M:%S')}                               ║")
print(f"║   Finished: {end_time.strftime('%H:%M:%S')}                               ║")
print(f"║   Duration: {duration} seconds                              ║")
print("╠══════════════════════════════════════════════════════╣")
print("║   Output:                                            ║")
print("║   📁 05_data/raw/     → 4 messy CSVs                ║")
print("║   📁 05_data/cleaned/ → 9 clean CSVs                ║")
print("╚══════════════════════════════════════════════════════╝")