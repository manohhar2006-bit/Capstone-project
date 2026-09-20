import pandas as pd



# Load raw scraped data


RAW_FILE = "data_pipeline/raw_books.csv"

df = pd.read_csv(RAW_FILE)


# Clean price


def clean_price(value):
    """
    Convert a raw price such as 'Â£45.17'
    into a numeric GBP value such as 45.17.
    """

    try:
        cleaned_value = str(value).replace("Â£", "").replace("£", "").strip()
        return float(cleaned_value)

    except (ValueError, TypeError):
        return pd.NA


df["price_gbp"] = df["price"].apply(clean_price)


# Show price conversion

print("=" * 60)
print("PRICE CLEANING")
print("=" * 60)

print()
print("Original price → price_gbp")

print(
    df[["price", "price_gbp"]].head(10).to_string(index=False)
)

print()
print("price_gbp data type:")
print(df["price_gbp"].dtype)

print()
print("Missing price_gbp values:")
print(df["price_gbp"].isna().sum())

# Clean star rating


rating_mapping = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


df["rating"] = df["star_rating"].map(rating_mapping)


# Show rating conversion


print()
print("=" * 60)
print("STAR RATING CLEANING")
print("=" * 60)

print()
print("Original star_rating → rating")

print(
    df[["star_rating", "rating"]]
    .drop_duplicates()
    .sort_values("rating")
    .to_string(index=False)
)

print()
print("rating data type:")
print(df["rating"].dtype)

print()
print("Missing rating values:")
print(df["rating"].isna().sum())

# Clean availability

def clean_availability(value):
    """
    Convert raw availability text into a boolean value.
    """

    try:
        normalized_value = str(value).strip().lower()

        if normalized_value == "in stock":
            return True

        if normalized_value == "out of stock":
            return False

        return pd.NA

    except (ValueError, TypeError):
        return pd.NA


df["in_stock"] = df["availability"].apply(
    clean_availability
)


# Show availability conversion

print()
print("=" * 60)
print("AVAILABILITY CLEANING")
print("=" * 60)

print()
print("Original availability → in_stock")

print(
    df[["availability", "in_stock"]]
    .drop_duplicates()
    .to_string(index=False)
)

print()
print("in_stock data type:")
print(df["in_stock"].dtype)

print()
print("Missing in_stock values:")
print(df["in_stock"].isna().sum())

# Convert GBP to INR using the required project rate

GBP_TO_INR = 105.50

df["price_inr"] = df["price_gbp"] * GBP_TO_INR


# Show currency conversion


print()
print("=" * 60)
print("GBP TO INR CONVERSION")
print("=" * 60)

print()
print("Conversion rate:")
print(f"1 GBP = {GBP_TO_INR:.2f} INR")

print()
print("price_gbp → price_inr")

print(
    df[["price_gbp", "price_inr"]]
    .head(10)
    .to_string(index=False)
)

print()
print("price_inr data type:")
print(df["price_inr"].dtype)

print()
print("Missing price_inr values:")
print(df["price_inr"].isna().sum())

# Create final cleaned dataset


cleaned_df = df[
    [
        "title",
        "price_gbp",
        "rating",
        "in_stock",
        "category",
        "price_inr",
    ]
].copy()


# Explicitly enforce required data types
cleaned_df["price_gbp"] = cleaned_df["price_gbp"].astype(float)
cleaned_df["rating"] = cleaned_df["rating"].astype(int)
cleaned_df["in_stock"] = cleaned_df["in_stock"].astype(bool)
cleaned_df["price_inr"] = cleaned_df["price_inr"].astype(float)



# Save cleaned dataset

cleaned_df.to_csv(
    "data_pipeline/cleaned_books.csv",
    index=False
)


# Final cleaned dataset verification

print()
print("=" * 60)
print("FINAL CLEANED DATASET")
print("=" * 60)

print()
print("Shape:")
print(cleaned_df.shape)

print()
print("Columns:")
print(cleaned_df.columns.tolist())

print()
print("Data types:")
print(cleaned_df.dtypes)

print()
print("Missing values:")
print(cleaned_df.isna().sum())

print()
print("First 5 cleaned rows:")
print(cleaned_df.head().to_string(index=False))

print()
print(
    "Cleaned data saved to data_pipeline/cleaned_books.csv"
)