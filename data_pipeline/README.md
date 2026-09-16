# Module 1 — Data Pipeline

## Overview

This module implements an end-to-end data pipeline for scraping, cleaning, converting, storing, and querying book catalogue data from Books to Scrape.

The pipeline follows this flow:

Raw website
→ scraping
→ raw CSV
→ cleaning and transformation
→ cleaned CSV
→ normalized SQLite database
→ SQL queries
→ pandas verification

---

## 1. Data Source

The data source used for this module is:

https://books.toscrape.com/

Books to Scrape is a public scraping-practice website that does not require login or an API key.

The scraper collects books from three categories:

- Travel
- Mystery
- Romance

The final scraped dataset contains:

- 11 Travel books
- 32 Mystery books
- 35 Romance books
- 78 books in total

This satisfies the project requirement of at least 60 books across at least 3 categories.

---

## 2. Raw Fields Collected

The scraper collects the following fields for every book:

- `title`
- `price`
- `star_rating`
- `availability`
- `category`

The scraping implementation is contained in:

`data_pipeline/scrape_books.py`

The scraper uses:

- `requests`
- `BeautifulSoup`

Pagination is followed automatically using the website's `next` link.

---

## 3. Raw Dataset

Running the scraper produces:

`data_pipeline/raw_books.csv`

The raw dataset contains:

- 78 rows
- 5 columns

The raw fields are preserved before cleaning.

---

## 4. Data Cleaning

Cleaning is implemented in:

`data_pipeline/clean_data.py`

### 4.1 Price

The raw `price` field contains the currency symbol.

Example:

`Â£45.17`

The currency symbol is removed and the value is converted to a floating-point number.

Example:

`Â£45.17 → 45.17`

The resulting column is:

`price_gbp`

Data type:

`float64`

All 78 values were successfully parsed.

No price values required missing-value handling.

---

### 4.2 Star Rating

The raw `star_rating` field contains textual values:

- One
- Two
- Three
- Four
- Five

These are converted to integer values:

- One → 1
- Two → 2
- Three → 3
- Four → 4
- Five → 5

The resulting column is:

`rating`

Data type:

`int64`

All 78 values were successfully converted.

---

### 4.3 Availability

The raw `availability` field contained:

`In stock`

The value is converted into the boolean column:

`in_stock`

The resulting value is:

`True`

Data type:

`bool`

All 78 values were successfully converted.

---

### 4.4 Currency Conversion

The project-required fixed conversion rate is:

`1 GBP = 105.50 INR`

This is a project-defined fixed baseline and is applied directly without using an external currency API.

The calculation is:

`price_inr = price_gbp × 105.50`

The resulting column is:

`price_inr`

Data type:

`float64`

All 78 values were successfully calculated.

---

## 5. Missing-Value Handling

The raw dataset was inspected before cleaning.

Missing-value counts were:

- `title`: 0
- `price`: 0
- `star_rating`: 0
- `availability`: 0
- `category`: 0

Therefore, no rows needed to be dropped or numeric values imputed for the current dataset.

The cleaning functions were still written defensively so that unexpected parsing failures do not crash the pipeline.

---

## 6. Duplicate Check

The raw dataset was checked for duplicate rows.

Duplicate rows found:

`0`

---

## 7. Cleaned Dataset

The final cleaned dataset is saved as:

`data_pipeline/cleaned_books.csv`

It contains:

- 78 rows
- 6 columns

Columns:

- `title`
- `price_gbp`
- `rating`
- `in_stock`
- `category`
- `price_inr`

The final dataset contains no missing values.

---

## 8. Database Design

The cleaned dataset is loaded into a normalized SQLite database:

`data_pipeline/zepto_books.db`

The database contains two tables.

### categories

| Column | Type | Constraint |
|---|---|---|
| category_id | INTEGER | PRIMARY KEY |
| category_name | TEXT | UNIQUE, NOT NULL |

### books

| Column | Type | Constraint |
|---|---|---|
| book_id | INTEGER | PRIMARY KEY |
| title | TEXT | NOT NULL |
| price_gbp | REAL | NOT NULL |
| price_inr | REAL | NOT NULL |
| rating | INTEGER | NOT NULL |
| in_stock | INTEGER | NOT NULL |
| category_id | INTEGER | FOREIGN KEY |

The foreign-key relationship is:

`books.category_id → categories.category_id`

SQLite stores the boolean `in_stock` values as:

- `1` for True
- `0` for False

The database was verified with:

- 3 category records
- 78 book records
- 0 invalid foreign-key references

---

## 9. Database Creation and Loading

Database creation and data loading are implemented in:

`data_pipeline/database.py`

The script:

1. Reads `cleaned_books.csv`
2. Creates the SQLite database
3. Creates the `categories` table
4. Creates the `books` table
5. Inserts the three categories
6. Inserts all 78 books
7. Connects every book to its category through `category_id`
8. Verifies the inserted records and foreign-key relationship

The database can therefore be regenerated from the script.

---

## 10. SQL Queries

SQL queries are stored in:

`data_pipeline/queries.sql`

Six queries are included.

### Query 1

Demonstrates:

`SELECT` + `WHERE`

Purpose:

List books with a rating of 5.

### Query 2

Demonstrates:

`ORDER BY` + `LIMIT`

Purpose:

Find the 10 most expensive books by GBP price.

### Query 3

Demonstrates:

`DISTINCT`

Purpose:

List the unique rating values.

### Query 4

Demonstrates:

`BETWEEN`

Purpose:

List books with prices between 20 and 40 GBP.

### Query 5

Demonstrates:

`IN`

Purpose:

List books belonging to the Travel or Mystery categories.

### Query 6

Demonstrates:

`JOIN`

Purpose:

Join the `books` and `categories` tables to return book details together with the category name.

---

## 11. SQL Query Outputs

The queries are executed by:

`data_pipeline/run_queries.py`

The generated SQL and query results are saved to:

`data_pipeline/query_outputs.txt`

The script executes all six queries directly against the SQLite database.

---

## 12. Pandas Verification

Pandas verification is implemented in:

`data_pipeline/pandas_verification.py`

Two SQL query results are loaded into pandas using:

`pd.read_sql()`

The database `books` and `categories` tables are also loaded into pandas DataFrames.

The SQL JOIN is then reproduced using:

`pd.merge()`

The SQL JOIN and pandas merge results were compared after applying equivalent ordering and limiting.

Verification result:

`Equivalent: True`

The verification output is saved to:

`data_pipeline/pandas_verification.txt`

---

## 13. Important Files

| File | Purpose |
|---|---|
| `scrape_books.py` | Scrapes the three categories |
| `raw_books.csv` | Raw scraped dataset |
| `clean_data.py` | Cleans and transforms the raw dataset |
| `cleaned_books.csv` | Final cleaned dataset |
| `database.py` | Creates and loads the SQLite database |
| `zepto_books.db` | SQLite database |
| `queries.sql` | Required SQL queries |
| `run_queries.py` | Executes SQL queries and saves outputs |
| `query_outputs.txt` | Saved SQL query outputs |
| `pandas_verification.py` | `pd.read_sql()` and `pd.merge()` verification |
| `pandas_verification.txt` | Saved pandas verification results |
| `inspect_raw.py` | Inspects the raw dataset |
| `verify_cleaned.py` | Verifies the cleaned dataset |
| `verify_database.py` | Verifies database schema and relationships |
| `requirements.txt` | Module 1 Python dependencies |

---

## 14. Installation

From the project root, activate the virtual environment.

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1