# BCPL Supply Chain Cost Leakage Diagnostic & Recovery Plan

**Company:** Bongo Consumer Products Ltd. (BCPL) — Fictional  
**Period:** January 2025 – December 2025  
**Date:** July 2026

---

## Executive Summary

Bongo Consumer Products Ltd. (BCPL) experienced a consistent rise in 
supply chain costs over the past year, with no clear visibility into 
the root causes. This diagnostic report identifies and quantifies 
hidden cost leakages across four supply chain functions — Procurement, 
Inventory, Logistics, and Order Fulfillment — and delivers a 
prioritized recovery action plan.

**Total identified leakage: ৳29.22 lakh (2,922,360 BDT)**

Key finding: 52.54% of total leakage originates from Procurement alone, 
driven by three import suppliers consistently charging above negotiated 
contract prices. Inventory dead stock accounts for a further 35.63%, 
concentrated in Sylhet and Chattogram regional depots.

By addressing the top 7 identified issues, BCPL can potentially recover 
an estimated ৳15.93 lakh (54.52% of total leakage) annually.

---

## 1. Procurement Leakage — ৳15.22 lakh (52.54%)

### Finding
317 out of 1,062 completed purchase orders were flagged for price 
variance exceeding the 5% threshold. Import suppliers consistently 
charged above negotiated contract prices, with the average variance 
reaching 6% across all suppliers.

Emergency and rush orders carried a significantly higher variance — 
20.8% and 17.1% respectively — compared to just 3.3% for regular 
orders, indicating that unplanned procurement is disproportionately 
expensive for BCPL.

### Top Offending Suppliers

| Supplier | Type | Avg Variance % | Total Leakage |
|---|---|---|---|
| MegaChem Corp | Import | 18.75% | ৳4,03,528 |
| GlobalPack Imports | Import | 16.80% | ৳2,87,066 |
| AsiaFood Commodities | Import | 11.51% | ৳2,39,877 |

These 3 suppliers (20% of total 15) account for 59.24% of total 
procurement leakage.

### Recommendations

**R1 — Re-negotiate MegaChem Corp contract (Priority: High)**
MegaChem Corp's consistent 18.75% price overcharge represents the 
single largest leakage source. BCPL should initiate contract 
renegotiation with a target of reducing variance to below 5%, or 
identify a local chemical supplier as an alternative source.
Estimated annual saving: ৳2,41,000

**R2 — Dual-source GlobalPack Imports (Priority: High)**
GlobalPack Imports consistently overcharges by 16.8%. Evaluating 
local packaging alternatives (e.g. Agropack Ltd., PolyPack Industries) 
as partial substitutes would reduce dependency on this import supplier.
Estimated annual saving: ৳1,72,000

**R3 — Renegotiate AsiaFood Commodities (Priority: Medium)**
At 11.51% average variance, AsiaFood Commodities represents a 
medium-priority renegotiation target. Alternative Thailand or local 
food ingredient suppliers should be evaluated.
Estimated annual saving: ৳1,44,000

**R4 — Reduce Rush/Emergency Orders (Priority: Medium)**
Emergency orders carry a 20.8% price variance — more than 6x regular 
orders. Improving procurement planning and demand forecasting would 
reduce the frequency of rush orders, directly reducing premium costs.
Estimated annual saving: Embedded in R1-R3 savings above.

---

## 2. Inventory Leakage — ৳10.65 lakh (35.63%)

### Finding
23.3% of all monthly inventory snapshots were flagged as dead stock 
(stock age exceeding 90 days). The average dead stock age was 126 days, 
indicating that slow-moving products remain in warehouses well beyond 
acceptable thresholds.

Total holding cost across all stock: ৳45.96 lakh — of which dead stock 
alone contributed ৳10.65 lakh (23.2% of total holding cost wasted).

### Dead Stock by Warehouse

| Warehouse | Dead Stock Leakage | % of Total |
|---|---|---|
| Sylhet Regional Depot | ৳3,61,305 | 33.92% |
| Chattogram Regional Hub | ৳3,00,354 | 28.20% |
| Khulna Distribution Center | ৳2,69,142 | 25.27% |
| Tejgaon Central Warehouse | ৳1,34,417 | 12.62% |

### Dead Stock by Product Category

| Category | Dead Stock Count | Leakage | Avg Age |
|---|---|---|---|
| Packaged Food | 204 | ৳5,31,314 | 132 days |
| Personal Care | 108 | ৳4,35,048 | 117 days |
| Home Care | 24 | ৳98,857 | 104 days |

### Recommendations

**R5 — Improve demand forecasting for Sylhet depot (Priority: High)**
Sylhet Regional Depot accounts for 33.92% of dead stock leakage — the 
highest among all warehouses. Rural distribution patterns in Sylhet 
cause stock to accumulate beyond demand. Implementing SKU-level demand 
forecasting for this depot would significantly reduce overstocking.
Estimated annual saving: ৳1,80,000

**R6 — SKU rationalization for Packaged Food (Priority: High)**
Packaged Food drives 49.88% of dead stock leakage, with an average 
dead stock age of 132 days — well beyond expiry risk thresholds. BCPL 
should review slow-moving Packaged Food SKUs and implement 
expiry-based ordering with shorter replenishment cycles.
Estimated annual saving: ৳1,50,000

---

## 3. Logistics Leakage — ৳2.68 lakh (9.58%)

### Finding
150 out of 800 shipments (18.75%) were delivered late, generating 
৳87,000 in penalties alone. Freight cost overruns across all routes 
contributed an additional ৳1,81,000, bringing total logistics leakage 
to ৳2,68,000.

The Route Risk Matrix analysis identified two routes as high-risk — 
simultaneously carrying high cost overruns and high late delivery rates.

### Logistics Leakage by Route

| Route | Avg Overrun % | Late % | Total Leakage |
|---|---|---|---|
| Dhaka–Sylhet Highway | 11.65% | 19.2% | ৳97,439 |
| Sylhet Tea Belt | 32.83% | 40.0% | ৳61,792 |
| Khulna–Jessore Belt | 20.64% | 34.9% | ৳57,429 |
| Dhaka–Chattogram Highway | 10.12% | 2.5% | ৳37,783 |

### Recommendations

**R7 — Route optimization for Sylhet Tea Belt (Priority: Medium)**
Sylhet Tea Belt has the highest late delivery rate (40%) and average 
cost overrun (32.83%). Route replanning and carrier SLA enforcement 
with penalty clauses would reduce both overrun and late delivery costs.
Estimated annual saving: ৳34,000

**R8 — Carrier review for Khulna–Jessore Belt (Priority: Low)**
Khulna–Jessore Belt generated the highest late penalty (৳28,500) 
despite moderate overrun. A carrier performance review with stricter 
SLA enforcement is recommended.
Estimated annual saving: ৳32,000

---

## 4. Fulfillment Leakage — ৳67,200 (2.25%)

### Finding
114 out of 1,062 fulfilled orders (10.7%) resulted in either a return 
or partial shipment. Partial shipments were the larger cost driver 
(৳52,800) compared to returns (৳14,400).

Khulna Distribution Center had the highest fulfillment error rate, 
with 24 partial shipments generating ৳19,200 in extra costs. Quality 
issues were the top return reason (11 cases).

### Note
Fulfillment leakage at 2.25% of total is the smallest category. 
Addressing Procurement and Inventory issues (R1-R6) should be 
prioritized before focusing on fulfillment process improvements.

---

## 5. Recovery Summary

| Priority | Recommendation | Category | Est. Saving |
|---|---|---|---|
| 1 | Re-negotiate MegaChem Corp | Procurement | ৳2,41,000 |
| 2 | Dual-source GlobalPack Imports | Procurement | ৳1,72,000 |
| 3 | Demand forecasting — Sylhet depot | Inventory | ৳1,80,000 |
| 4 | Route optimization — Sylhet Tea Belt | Logistics | ৳34,000 |
| 5 | Renegotiate AsiaFood Commodities | Procurement | ৳1,44,000 |
| 6 | SKU rationalization — Packaged Food | Inventory | ৳1,50,000 |
| 7 | Carrier review — Khulna–Jessore | Logistics | ৳32,000 |
| | **Total Estimated Recovery** | | **৳9,53,000** |

**Total Identified Leakage: ৳29,22,360**
**Estimated Recoverable: ৳15,93,184 (54.52%)**

---

## 6. Assumptions & Limitations

- All data is synthetically generated for portfolio demonstration purposes
- Cost assumptions (holding rate 2%, late penalty ৳500, return cost 
  ৳300, partial cost ৳800) are illustrative estimates
- Savings estimates assume 50-60% recovery of identified leakage — 
  actual savings depend on negotiation outcomes and operational changes
- Analysis covers January–December 2025 only

---

*This report was produced as part of a data analytics portfolio project. 
All company names, figures, and scenarios are fictional.*
