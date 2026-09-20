import sqlite3
from pathlib import Path

import pandas as pd

# Configuration

DATABASE_PATH = "data_pipeline/zepto_books.db"
OUTPUT_FILE = "data_pipeline/pandas_verification.txt"


# Connect to SQLite
connection = sqlite3.connect(DATABASE_PATH)

# SQL Query 1
# Use pd.read_sql()

query_1 = """
SELECT
    book_id,
    title,
    rating,
    price_gbp,
    category_id
FROM books
WHERE rating = 5;
"""


df_query_1 = pd.read_sql(
    query_1,
    connection
)

# SQL Query 2
# Use pd.read_sql()

query_2 = """
SELECT
    book_id,
    title,
    price_gbp,
    rating,
    category_id
FROM books
ORDER BY price_gbp DESC
LIMIT 10;
"""


df_query_2 = pd.read_sql(
    query_2,
    connection
)


# SQL JOIN Query
# This reproduces Query 6 from queries.sql


join_query = """
SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books AS b
JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY c.category_name, b.rating DESC, b.title
LIMIT 10;
"""


df_sql_join = pd.read_sql(
    join_query,
    connection
)


# Read the source tables into pandas

books_df = pd.read_sql(
    """
    SELECT
        book_id,
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock,
        category_id
    FROM books;
    """,
    connection
)


categories_df = pd.read_sql(
    """
    SELECT
        category_id,
        category_name
    FROM categories;
    """,
    connection
)


# Reproduce the JOIN using pandas merge()

df_pandas_join = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)

# Apply the same ordering as the SQL JOIN query

df_pandas_join = df_pandas_join.sort_values(
    by=[
        "category_name",
        "rating",
        "title"
    ],
    ascending=[
        True,
        False,
        True
    ]
)

# Apply the same LIMIT 10 as the SQL query

df_pandas_join = df_pandas_join.head(10)


# Select the same columns and order as SQL
df_pandas_join = df_pandas_join[
    [
        "book_id",
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category_name"
    ]
]


# Reset indexes for comparison
df_sql_join = df_sql_join.reset_index(drop=True)

df_pandas_join = df_pandas_join.reset_index(drop=True)


# Compare SQL JOIN and pandas merge()
sql_join_result = df_sql_join.copy()

pandas_join_result = df_pandas_join.copy()


# Normalize numeric precision before comparison
sql_join_result["price_gbp"] = sql_join_result["price_gbp"].round(6)
pandas_join_result["price_gbp"] = pandas_join_result["price_gbp"].round(6)

sql_join_result["price_inr"] = sql_join_result["price_inr"].round(6)
pandas_join_result["price_inr"] = pandas_join_result["price_inr"].round(6)


joins_are_equivalent = sql_join_result.equals(
    pandas_join_result
)


# Print results
print("=" * 70)
print("PANDAS VERIFICATION")
print("=" * 70)


print()
print("READ_SQL QUERY 1: RATING = 5")
print()
print(df_query_1.to_string(index=False))


print()
print("READ_SQL QUERY 2: TOP 10 MOST EXPENSIVE")
print()
print(df_query_2.to_string(index=False))


print()
print("=" * 70)
print("SQL JOIN RESULT")
print("=" * 70)
print()
print(sql_join_result.to_string(index=False))


print()
print("=" * 70)
print("PANDAS MERGE RESULT")
print("=" * 70)
print()
print(pandas_join_result.to_string(index=False))


print()
print("=" * 70)
print("JOIN EQUIVALENCE CHECK")
print("=" * 70)

print()
print("SQL JOIN rows:", len(sql_join_result))
print("Pandas merge rows:", len(pandas_join_result))
print("Equivalent:", joins_are_equivalent)


# Save verification output
output_sections = []

output_sections.append("=" * 70)
output_sections.append("PANDAS VERIFICATION")
output_sections.append("=" * 70)

output_sections.append("")
output_sections.append("READ_SQL QUERY 1: RATING = 5")
output_sections.append("")
output_sections.append(
    df_query_1.to_string(index=False)
)

output_sections.append("")
output_sections.append(
    "READ_SQL QUERY 2: TOP 10 MOST EXPENSIVE"
)

output_sections.append("")
output_sections.append(
    df_query_2.to_string(index=False)
)

output_sections.append("")
output_sections.append("=" * 70)
output_sections.append("SQL JOIN RESULT")
output_sections.append("=" * 70)
output_sections.append("")
output_sections.append(
    sql_join_result.to_string(index=False)
)

output_sections.append("")
output_sections.append("=" * 70)
output_sections.append("PANDAS MERGE RESULT")
output_sections.append("=" * 70)
output_sections.append("")
output_sections.append(
    pandas_join_result.to_string(index=False)
)

output_sections.append("")
output_sections.append("=" * 70)
output_sections.append("JOIN EQUIVALENCE CHECK")
output_sections.append("=" * 70)
output_sections.append("")
output_sections.append(
    f"SQL JOIN rows: {len(sql_join_result)}"
)
output_sections.append(
    f"Pandas merge rows: {len(pandas_join_result)}"
)
output_sections.append(
    f"Equivalent: {joins_are_equivalent}"
)


Path(OUTPUT_FILE).write_text(
    "\n".join(output_sections),
    encoding="utf-8"
)


# Close connection
connection.close()


print()
print(
    f"Verification saved to: {OUTPUT_FILE}"
)