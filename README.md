# Sales Demand Forecasting for a Local Shop

Estimates future demand for a small grocery shop from its past sales, so the owner
knows what to restock and when.

> **The data is generated sample data, not real shop records.** `generate_data.py`
> builds 22 months of sales with realistic patterns built in: yearly growth, a
> Diwali peak, summer demand for cold drinks, winter demand for tea, and busier
> weekends. Because the patterns are known, it is possible to check that the
> analysis actually finds them. A real shop's billing export would work with the
> same code.

## Status

| Step | Script | Status |
|---|---|---|
| 1. Setup check | `check_setup.py` | Done |
| 2. Sample dataset | `generate_data.py` | Done |
| 3. SQLite database | `create_database.py` | Done |
| 4. Data cleaning | `clean_data.py` | Done |
| 5. Analysis and charts | | Planned |
| 6. Forecasting (moving average vs linear regression, MAE) | | Planned |
| 7. Streamlit dashboard | | Planned |

## Tech stack

- **Python 3**
- **pandas** for loading, cleaning and grouping data
- **scikit-learn** for linear regression and the MAE error measure
- **matplotlib** for charts
- **Streamlit** for the dashboard
- **SQLite** (built into Python) for a single-file SQL database

## Run it

```bash
pip install -r requirements.txt
python check_setup.py        # checks libraries, creates data/ and charts/
python generate_data.py      # writes data/products.csv, raw_sales.csv, stock.csv
python create_database.py    # builds data/shop.db and reports data problems
python clean_data.py         # removes duplicates, blanks, negatives, bad dates
```

## Data

| File | Contents |
|---|---|
| `data/products.csv` | 12 grocery products: name, category, price |
| `data/raw_sales.csv` | ~7,800 daily sales totals per product, Jan 2025 to Oct 2026 |
| `data/stock.csv` | Current stock and reorder level per product |

Daily quantities are drawn from a Poisson distribution, because they are counts.
The random seed is fixed (`42`), so every run produces the same data.

The raw sales deliberately contain errors so the cleaning step has something to
fix: about 1% blank quantities, 20 negative quantities, 10 impossible dates and
about 1.5% duplicate rows.

## Database

`create_database.py` loads the CSVs into `data/shop.db`:

```
products (product_id PK, name, category, price)
sales    (sale_id PK, sale_date, product_id FK -> products, quantity)
stock    (product_id PK/FK -> products, current_stock, reorder_level)
```

`data/shop.db` is generated, so it is not stored in the repository. Run the scripts
above to create it.

## Limits

The forecast is a trend estimate based on past sales, not a guaranteed prediction.
Its error (MAE) is measured to show how far off it can be.

## License

[MIT](LICENSE)
