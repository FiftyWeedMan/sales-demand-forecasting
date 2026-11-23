# clean_data.py
# Step 4: Clean the raw sales data and save the clean version back
#         into the 'sales' table of data/shop.db.
# The original raw data is still kept in data/raw_sales.csv.

import sqlite3
import pandas as pd

conn = sqlite3.connect("data/shop.db")

# ---------- 1. Read raw sales from the database using SQL ----------
sales = pd.read_sql_query("SELECT * FROM sales", conn)
before = len(sales)
log = []   # we record how many rows each step removes

# ---------- 2. Remove duplicate rows ----------
# Same date + same product + same quantity = the same entry saved twice
n = len(sales)
sales = sales.drop_duplicates(subset=["sale_date", "product_id", "quantity"], keep="first")
log.append(("Duplicate rows removed", n - len(sales)))

# ---------- 3. Remove rows with missing quantity ----------
# We can't know the real number, and it's only ~1% of rows, so we drop them
n = len(sales)
sales = sales.dropna(subset=["quantity"])
log.append(("Missing quantity removed", n - len(sales)))

# ---------- 4. Remove negative quantities ----------
# A sale can't be negative; could be a typo or a return - we can't be sure
n = len(sales)
sales = sales[sales["quantity"] > 0]
log.append(("Negative quantity removed", n - len(sales)))

# ---------- 5. Remove impossible dates ----------
# errors="coerce" turns invalid dates (like month 13) into NaT (= "not a time")
n = len(sales)
sales["sale_date"] = pd.to_datetime(sales["sale_date"], format="%Y-%m-%d", errors="coerce")
sales = sales.dropna(subset=["sale_date"])
log.append(("Invalid dates removed", n - len(sales)))

# ---------- 6. Fix data types ----------
sales["quantity"] = sales["quantity"].astype(int)                 # 6.0 -> 6
sales["sale_date"] = sales["sale_date"].dt.strftime("%Y-%m-%d")    # back to text for SQLite

# ---------- 7. Save clean data back into the sales table ----------
# DELETE + append keeps the table structure (primary key, foreign key) intact
conn.execute("DELETE FROM sales")
sales.to_sql("sales", conn, if_exists="append", index=False)
conn.commit()

# ---------- 8. Report ----------
print("CLEANING REPORT")
print(f"{'Rows before cleaning':<28}{before:>6}")
for step, removed in log:
    print(f"{step:<28}{removed:>6}")
print(f"{'Rows after cleaning':<28}{len(sales):>6}")
print(f"{'% of data kept':<28}{len(sales) / before * 100:>5.1f}%")

# Check with SQL that no problems are left
check = pd.read_sql_query("""
    SELECT SUM(quantity IS NULL) AS missing_qty,
           SUM(quantity <= 0)    AS bad_qty,
           SUM(date(sale_date) IS NULL) AS bad_dates
    FROM sales
""", conn)
print("\nProblems left (should all be 0):")
print(check.to_string(index=False))

print("\nSample of clean data:")
print(pd.read_sql_query("""
    SELECT s.sale_date, p.name, CAST(s.quantity AS INTEGER) AS quantity
    FROM sales s JOIN products p ON s.product_id = p.product_id
    ORDER BY s.sale_date LIMIT 5
""", conn).to_string(index=False))

conn.close()
