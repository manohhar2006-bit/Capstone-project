import sqlite3
import pandas as pd


# =========================================================
# Configuration
# =========================================================

DATABASE_PATH = "data_pipeline/zepto_books.db"
CLEANED_FILE = "data_pipeline/cleaned_books.csv"


# =========================================================
# Load cleaned dataset
# =========================================================

cleaned_df = pd.read_csv(CLEANED_FILE)


# =========================================================
# Connect to SQLite database
# =========================================================

connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()


# =========================================================
# Enable foreign-key enforcement
# =========================================================

cursor.execute("PRAGMA foreign_keys = ON;")


# =========================================================
# Recreate database tables from scratch
# =========================================================
# Dropping the tables first makes this script reproducible.
# Every run starts with a clean database and avoids duplicate
# book records.
# =========================================================

cursor.execute("DROP TABLE IF EXISTS books;")
cursor.execute("DROP TABLE IF EXISTS categories;")

connection.commit()


# =========================================================
# Create categories table
# =========================================================

cursor.execute(
    """
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT UNIQUE NOT NULL
    );
    """
)


# =========================================================
# Create books table
# =========================================================

cursor.execute(
    """
    CREATE TABLE books (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price_gbp REAL NOT NULL,
        price_inr REAL NOT NULL,
        rating INTEGER NOT NULL,
        in_stock INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id)
            REFERENCES categories(category_id)
    );
    """
)

connection.commit()


# =========================================================
# Insert categories
# =========================================================

categories = [
    ("Travel",),
    ("Mystery",),
    ("Romance",),
]

cursor.executemany(
    """
    INSERT INTO categories (category_name)
    VALUES (?);
    """,
    categories
)

connection.commit()


# =========================================================
# Read category IDs from database
# =========================================================

cursor.execute(
    """
    SELECT category_id, category_name
    FROM categories
    ORDER BY category_id;
    """
)

category_lookup = {
    category_name: category_id
    for category_id, category_name in cursor.fetchall()
}


# =========================================================
# Prepare book records
# =========================================================

book_records = []

for _, row in cleaned_df.iterrows():

    category_name = row["category"]

    category_id = category_lookup[category_name]

    book_records.append(
        (
            row["title"],
            float(row["price_gbp"]),
            float(row["price_inr"]),
            int(row["rating"]),
            int(bool(row["in_stock"])),
            category_id,
        )
    )


# =========================================================
# Insert books
# =========================================================

cursor.executemany(
    """
    INSERT INTO books (
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock,
        category_id
    )
    VALUES (?, ?, ?, ?, ?, ?);
    """,
    book_records
)

connection.commit()


# =========================================================
# Verify tables
# =========================================================

cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """
)

tables = cursor.fetchall()


# =========================================================
# Verify category records
# =========================================================

cursor.execute(
    """
    SELECT category_id, category_name
    FROM categories
    ORDER BY category_id;
    """
)

category_rows = cursor.fetchall()


# =========================================================
# Verify book count
# =========================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM books;
    """
)

book_count = cursor.fetchone()[0]


# =========================================================
# Verify books per category
# =========================================================

cursor.execute(
    """
    SELECT
        c.category_name,
        COUNT(b.book_id) AS book_count
    FROM categories AS c
    LEFT JOIN books AS b
        ON c.category_id = b.category_id
    GROUP BY c.category_id, c.category_name
    ORDER BY c.category_id;
    """
)

books_per_category = cursor.fetchall()


# =========================================================
# Verify foreign-key integrity
# =========================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM books
    WHERE category_id NOT IN (
        SELECT category_id
        FROM categories
    );
    """
)

invalid_foreign_keys = cursor.fetchone()[0]


# =========================================================
# Print verification results
# =========================================================

print("=" * 60)
print("DATABASE CREATED AND LOADED")
print("=" * 60)

print()
print("Database file:")
print(DATABASE_PATH)

print()
print("Tables:")

for table in tables:
    print("-", table[0])


print()
print("Categories:")

for category_id, category_name in category_rows:
    print(f"{category_id}: {category_name}")


print()
print("Total books inserted:")
print(book_count)


print()
print("Books by category:")

for category_name, count in books_per_category:
    print(f"{category_name}: {count}")


print()
print("Invalid foreign-key references:")
print(invalid_foreign_keys)


# =========================================================
# Close database connection
# =========================================================

connection.close()