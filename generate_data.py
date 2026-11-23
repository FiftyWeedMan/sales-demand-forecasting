# generate_data.py
# Step 2: Create SAMPLE (generated) sales data for a local grocery shop.
# NOTE: This is NOT real shop data. It is generated with realistic patterns
#       (trend + seasonality + randomness) so we can build and test the system.

import numpy as np
import pandas as pd

np.random.seed(42)   # fixed seed = same "random" data every time we run it

# ---------- 1. Products ----------
# product_id, name, category, price (Rs), base daily sales, yearly growth
products = pd.DataFrame([
    (1,  "Rice 5kg",          "Staples",   350, 4.0,  0.05),
    (2,  "Wheat Atta 10kg",   "Staples",   420, 3.5,  0.03),
    (3,  "Sugar 1kg",         "Staples",    45, 6.0,  0.00),
    (4,  "Toor Dal 1kg",      "Staples",   160, 3.0,  0.04),
    (5,  "Mustard Oil 1L",    "Staples",   180, 3.0,  0.02),
    (6,  "Tea 250g",          "Beverages", 140, 2.5,  0.06),
    (7,  "Cold Drink 1L",     "Beverages",  60, 3.0,  0.15),
    (8,  "Biscuits Pack",     "Snacks",     30, 8.0,  0.10),
    (9,  "Namkeen 400g",      "Snacks",     90, 3.0,  0.08),
    (10, "Bathing Soap",      "Personal",   40, 5.0, -0.05),
    (11, "Detergent 1kg",     "Household", 120, 2.5,  0.02),
    (12, "Milk Powder 500g",  "Dairy",     240, 1.5, -0.10),
], columns=["product_id", "name", "category", "price", "base", "growth"])

# ---------- 2. Seasonality (month -> multiplier) ----------
# Festival season (Oct-Nov: Diwali) boosts sweets/snacks/oil/sugar,
# summer (Apr-Jun) boosts cold drinks, winter (Dec-Feb) boosts tea.
def season_factor(category, name, month):
    f = 1.0
    if month in (10, 11) and (category == "Snacks" or name in ("Sugar 1kg", "Mustard Oil 1L")):
        f *= 1.6                               # Diwali / festival rush
    if name == "Cold Drink 1L":
        f *= {4: 1.6, 5: 2.0, 6: 1.8, 12: 0.5, 1: 0.5}.get(month, 1.0)
    if name == "Tea 250g":
        f *= {12: 1.4, 1: 1.5, 2: 1.3, 5: 0.8, 6: 0.8}.get(month, 1.0)
    return f

# ---------- 3. Daily sales: Jan 2025 to Oct 2026 (22 months) ----------
dates = pd.date_range("2025-01-01", "2026-10-31", freq="D")
rows = []
for d in dates:
    years_passed = (d - dates[0]).days / 365          # for the growth trend
    weekend = 1.3 if d.day_of_week >= 5 else 1.0        # more customers on Sat/Sun
    for p in products.itertuples():
        mean = p.base * (1 + p.growth) ** years_passed * season_factor(p.category, p.name, d.month) * weekend
        qty = np.random.poisson(mean)                 # random whole number around the mean
        if qty > 0:
            rows.append([d.strftime("%Y-%m-%d"), p.product_id, qty])

sales = pd.DataFrame(rows, columns=["sale_date", "product_id", "quantity"])
sales["quantity"] = sales["quantity"].astype(float)   # float so we can insert missing values

# ---------- 4. Add deliberate data problems (for the cleaning step) ----------
n = len(sales)
# a) 1% missing quantities (like a blank cell in a bill entry)
idx = np.random.choice(n, int(n * 0.01), replace=False)
sales.loc[idx, "quantity"] = np.nan
# b) 20 negative quantities (data-entry typos)
idx = np.random.choice(n, 20, replace=False)
sales.loc[idx, "quantity"] = -sales.loc[idx, "quantity"].abs()
# c) 10 wrong dates (typos like month 13)
idx = np.random.choice(n, 10, replace=False)
sales.loc[idx, "sale_date"] = "2025-13-05"
# d) ~1.5% duplicate rows (same entry saved twice)
dupes = sales.sample(frac=0.015, random_state=1)
sales = pd.concat([sales, dupes]).sample(frac=1, random_state=2).reset_index(drop=True)
sales.insert(0, "sale_id", range(1, len(sales) + 1))

# ---------- 5. Current stock (as on 31 Oct 2026) ----------
stock = pd.DataFrame({
    "product_id":    products["product_id"],
    "current_stock": [120, 140, 60, 90, 70, 80, 150, 220, 40, 160, 75, 55],
    "reorder_level": [ 40,  35, 60, 30, 30, 25,  30,  80, 30,  50, 25, 15],
})

# ---------- 6. Save as CSV files ----------
products[["product_id", "name", "category", "price"]].to_csv("data/products.csv", index=False)
sales.to_csv("data/raw_sales.csv", index=False)
stock.to_csv("data/stock.csv", index=False)

print("SAMPLE DATA GENERATED (not real shop data)")
print(f"Period: {dates[0].date()} to {dates[-1].date()} ({len(dates)} days)")
print(f"Products: {len(products)}   Sales rows: {len(sales)}")
print("\nFirst 5 sales rows:")
print(sales.head().to_string(index=False))
print("\nProducts:")
print(products[["product_id", "name", "category", "price"]].to_string(index=False))
print("\nFiles saved: data/products.csv, data/raw_sales.csv, data/stock.csv")
