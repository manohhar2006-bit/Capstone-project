import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


# ---------------------------------------------------------
# Category configuration
# ---------------------------------------------------------

CATEGORIES = {
    "Travel": "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "Mystery": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "Romance": "https://books.toscrape.com/catalogue/category/books/romance_8/index.html",
}


# ---------------------------------------------------------
# Store all scraped books
# ---------------------------------------------------------

books = []


# ---------------------------------------------------------
# Scrape each category
# ---------------------------------------------------------

for category_name, start_url in CATEGORIES.items():

    print()
    print("=" * 60)
    print(f"Starting category: {category_name}")
    print("=" * 60)

    current_url = start_url
    page_number = 1

    while True:

        # Request the current page
        response = requests.get(
            current_url,
            timeout=10
        )

        # Stop if the website returns an HTTP error
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Find all books on the current page
        book_cards = soup.select(
            "article.product_pod"
        )

        print(
            f"Scraping {category_name} - "
            f"Page {page_number} - "
            f"{len(book_cards)} books"
        )

        # -------------------------------------------------
        # Extract each book
        # -------------------------------------------------

        for book in book_cards:

            # Full title from the HTML title attribute
            title = book.select_one(
                "h3 a"
            )["title"]

            # Raw price exactly as scraped
            price = book.select_one(
                "p.price_color"
            ).get_text(
                strip=True
            )

            # Star rating text:
            # One, Two, Three, Four, or Five
            star_rating = book.select_one(
                "p.star-rating"
            )["class"][1]

            # Availability text:
            # e.g. "In stock"
            availability = book.select_one(
                "p.availability"
            ).get_text(
                " ",
                strip=True
            )

            # Store one complete raw record
            book_data = {
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category_name,
            }

            books.append(book_data)

        # -------------------------------------------------
        # Check whether another page exists
        # -------------------------------------------------

        next_page = soup.find(
            "li",
            class_="next"
        )

        # No "next" button means this is the last page
        if next_page is None:
            break

        next_link = next_page.find("a")

        # Safety check
        if next_link is None:
            break

        # Build the next page URL safely
        current_url = urljoin(
            current_url,
            next_link["href"]
        )

        page_number += 1


# ---------------------------------------------------------
# Scraping summary
# ---------------------------------------------------------

print()
print("=" * 60)
print("SCRAPING COMPLETE")
print("=" * 60)

print(
    f"Total books scraped: {len(books)}"
)

print()
print("Books by category:")

for category_name in CATEGORIES:

    category_count = sum(
        1
        for book in books
        if book["category"] == category_name
    )

    print(
        f"{category_name}: {category_count}"
    )


# ---------------------------------------------------------
# Convert raw records to pandas DataFrame
# ---------------------------------------------------------

raw_df = pd.DataFrame(books)


# ---------------------------------------------------------
# Save raw scraped data
# ---------------------------------------------------------

raw_df.to_csv(
    "data_pipeline/raw_books.csv",
    index=False
)

print()
print(
    "Raw data saved to data_pipeline/raw_books.csv"
)


# ---------------------------------------------------------
# Final verification
# ---------------------------------------------------------

print()
print("Raw dataset shape:", raw_df.shape)

print()
print("Raw dataset columns:")

for column in raw_df.columns:
    print(f"- {column}")