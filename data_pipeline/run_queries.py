import sqlite3
from pathlib import Path

# Configuration
DATABASE_PATH = "data_pipeline/zepto_books.db"
QUERY_FILE = "data_pipeline/queries.sql"
OUTPUT_FILE = "data_pipeline/query_outputs.txt"

# Read SQL file
query_text = Path(QUERY_FILE).read_text(
    encoding="utf-8"
)


# Split the SQL file into individual queries
queries = []

for statement in query_text.split(";"):

    statement = statement.strip()

    if not statement:
        continue

    # Remove comment-only lines from the beginning
    lines = statement.splitlines()

    sql_lines = [
        line
        for line in lines
        if not line.strip().startswith("--")
    ]

    sql = "\n".join(sql_lines).strip()

    if sql:
        queries.append(sql)

# Connect to database
connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()


# Store all output in memory
all_output = []

all_output.append("=" * 70)
all_output.append("ZEpto DATA & AI PLATFORM - MODULE 1")
all_output.append("SQL QUERY RESULTS")
all_output.append("=" * 70)
all_output.append("")


# Execute each query
for query_number, query in enumerate(queries, start=1):

    print()
    print("=" * 70)
    print(f"QUERY {query_number}")
    print("=" * 70)

    print()
    print("SQL:")
    print(query)

    cursor.execute(query)

    results = cursor.fetchall()

    column_names = [
        description[0]
        for description in cursor.description
    ]

    print()
    print("Columns:")
    print(column_names)

    print()
    print("Results:")

    if results:
        for row in results:
            print(row)
    else:
        print("No rows returned.")

    print()
    print("Number of rows:", len(results))

    # Save output for this query
    all_output.append("=" * 70)
    all_output.append(f"QUERY {query_number}")
    all_output.append("=" * 70)
    all_output.append("")
    all_output.append("SQL:")
    all_output.append(query)
    all_output.append("")
    all_output.append("Columns:")
    all_output.append(str(column_names))
    all_output.append("")
    all_output.append("Results:")

    if results:
        for row in results:
            all_output.append(str(row))
    else:
        all_output.append("No rows returned.")

    all_output.append("")
    all_output.append(f"Number of rows: {len(results)}")
    all_output.append("")


# Save all query outputs
Path(OUTPUT_FILE).write_text(
    "\n".join(all_output),
    encoding="utf-8"
)


# Close database
connection.close()


print()
print("=" * 70)
print("ALL QUERIES EXECUTED")
print("=" * 70)

print()
print(f"Total queries executed: {len(queries)}")

print()
print(
    f"Query outputs saved to: {OUTPUT_FILE}"
)