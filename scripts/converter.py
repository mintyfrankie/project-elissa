"""
A converter for converting the json-formatted data to the csv-formatted data.
"""

from pathlib import Path

import pandas as pd

from mongodb.client import DatabaseClient
from scraping.utils import ProductItem

DATA_PATH = Path(__file__).parent.parent / "data"


def export_products():
    """Export the products data."""

    db = DatabaseClient()
    assert db.check_connection(), "Database connection failed."

    project = {key: 1 for key in ProductItem.__annotations__}
    project["_id"] = 0

    EXCLUDED_KEYS = ["_metadata", "review_url"]
    for key in EXCLUDED_KEYS:
        project.pop(key)

    products = db.collection.find({}, project)
    products = list(products)
    products = pd.DataFrame(products)

    print(f"Queried {len(products)} products.")

    with open(DATA_PATH / "products.csv", "w") as file:
        products.to_csv(file, index=False)
        print("Exported products data.")

    db.close()
    return products


def export_reviews():
    """Export the reviews data."""

    db = DatabaseClient()
    assert db.check_connection(), "Database connection failed."

    project = {"_id": 0, "reviews": 1, "asin": 1}

    items = db.collection.find({}, project)
    items = list(items)

    def rowify_reviews(item):
        reviews = item["reviews"]
        asin = item["asin"]
        for review in reviews:
            review["asin"] = asin
            yield review

    items = [review for item in items for review in rowify_reviews(item)]
    reviews = pd.DataFrame(items)
    reviews = reviews[["asin"] + [col for col in reviews.columns if col != "asin"]]
    print(f"Queried {len(reviews)} reviews.")

    with open(DATA_PATH / "reviews.csv", "w") as file:
        reviews.to_csv(file, index=False)
        print("Exported reviews data.")

    return reviews
