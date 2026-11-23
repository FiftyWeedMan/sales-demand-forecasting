# create_database.py
# Step 3: Create the SQLite database (data/shop.db) with 3 tables
#         and load the sample data into it.

import sqlite3
import pandas as pd

conn = sqlite3.connect("data/shop.db")   # creates the file if it doesn't exist
cur = conn.cursor()

# ---------- 1. Create tables (drop old ones so we can re-run safely) ----------
cur.executescript("""
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS products;

-- Master list of products
CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL          -- price in Rs
);

-- One row = total quantity of one product sold on one day
CREATE TABLE sales (
    sale_id     INTEGER PRIMARY KEY,
    sale_date   TEXT,                     -- format YYYY-MM-DD
    product_id  INTEGER,
    quantity    REAL,                     -- may be blank/wrong in raw data
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Current stock of each product
CREATE TABLE stock (
    product_id    INTEGER PRIMARY KEY,
    current_stock INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,       -- reorder when stock falls below this
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# ---------- 2. Load CSV files into the tables ----------
products = pd.read_csv("data/products.csv")
sales    = pd.read_csv("data/raw_sales.csv")
stock    = pd.read_csv("data/stock.csv")

# if_exists="append" = put rows into the table we created above
products.to_sql("products", conn, if_exists="append", index=False)
sales.to_sql("sales", conn, if_exists="append", index=False)
stock.to_sql("stock", conn, if_exists="append", index=False)
conn.commit()
print("Database created: data/shop.db\n")

# ---------- 3. Run some SQL queries to check ----------
def show(title, sql):
    print("--- " + title + " ---")
    print(pd.read_sql_query(sql, conn).to_string(index=False))
    print()

show("Rows in each table", """
    SELECT 'products' AS table_name, COUNT(*) AS rows FROM products
    UNION ALL SELECT 'sales', COUNT(*) FROM sales
    UNION ALL SELECT 'stock', COUNT(*) FROM stock
""")

show("Sample sales joined with product names (JOIN)", """
    SELECT s.sale_date, p.name, s.quantity, p.price
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    ORDER BY s.sale_id
    LIMIT 5
""")

show("Data problems in raw sales (to fix in Step 4)", """
    SELECT
      SUM(quantity IS NULL)                      AS missing_qty,
      SUM(quantity < 0)                          AS negative_qty,
      SUM(date(sale_date) IS NULL)               AS bad_dates,
      COUNT(*) - (SELECT COUNT(*) FROM
                   (SELECT DISTINCT sale_date, product_id, quantity FROM sales))
                                                 AS duplicate_rows
    FROM sales
""")

conn.close()
