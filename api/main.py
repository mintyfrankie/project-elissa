"""
Contains the main function for the API.
"""

# TODO: add pytest cases for the API

from datetime import datetime

from fastapi import FastAPI, HTTPException, Path, Security
from fastapi.security.api_key import APIKey, APIKeyHeader

from mongodb import DatabaseClient
from scraping.common import get_driver
from scraping.product_page.spider import ProductItemScraper
from scraping.review_page.spider import ReviewItemScraper

app = FastAPI()
db = DatabaseClient()

api_keys = [
    "a1b2c3d4e5f6g7h8i9j0",
    "0j9i8h7g6f5e4d3c2b1a",
]
api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(header: str = Security(api_key_header)) -> str:
    """Check if the API key is valid."""

    if header in api_keys:
        return header
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )


asin_validator = Path(
    ...,
    title="ASIN",
    description="The ASIN of the product.",
    regex=r"[A-Z0-9]{10}",
)


@app.get("/api/product/all")
async def get_all_product_asins():
    """
    Get all ASINs from the database.
    """

    pipeline = [
        {
            "$project": {
                "_id": 0,
                "asin": 1,
            }
        }
    ]
    asins = list(db.collection.aggregate(pipeline))
    return asins


@app.get("/api/product/{asin}")
async def query_product(asin: str = asin_validator):
    """
    Query the product table for the given ASIN.
    """

    product = db.find_product(asin)
    if product is None:
        return {"error": "Product not found."}

    EXCLUDED_FIELDS = ["_id", "_metadata"]
    for field in EXCLUDED_FIELDS:
        product.pop(field, None)
    return product


@app.get("/api/product/search")
async def search_product(
    category: str, min_price: float | None, max_price: float | None
):
    """Search for products in the database according to the given parameters."""
    pipeline = [
        {
            "$match": {
                "category": category,
                "price": {"$gte": min_price, "$lte": max_price},
            }
        },
        {
            "$project": {
                "_id": 0,
                "_metadata": 0,
            }
        },
    ]
    products = list(db.collection.aggregate(pipeline))
    return products


@app.get("/api/scrape/product/{asin}")
async def scrape_product(
    asin: str = asin_validator, api_key: APIKey = Security(get_api_key)
) -> dict:  # ignore: W0613
    """
    Scrape the product page for the given ASIN.
    """

    driver = get_driver(driver_type="Chrome")
    url = f"https://www.amazon.fr/dp/{asin}"
    scraper = ProductItemScraper(driver, url)
    scraper.run()
    product = scraper.dump()
    if not scraper.validate():
        raise HTTPException(status_code=500, detail="Scraper failed.")
    return product


@app.get("/api/scrape/review/{asin}")
def scrape_review(
    asin: str = asin_validator,
    max_page: int = 5,
    api_key: APIKey = Security(get_api_key),  # ignore: W0613
):
    """
    Scrape the review page for the given ASIN.
    """

    driver = get_driver(driver_type="Chrome")
    url = f"https://www.amazon.fr/product-reviews/{asin}"
    scraper = ReviewItemScraper(driver, url, max_page=max_page)
    scraper.run()
    reviews = scraper.dump()
    if not scraper.validate():
        raise HTTPException(status_code=500, detail="Scraper failed.")
    return reviews


@app.post("/api/submit/product")
def submit_product(
    asin: str = asin_validator, api_key: APIKey = Security(get_api_key)
):  # ignore: W0613
    """
    Submit a new request to scrape all the information for the given ASIN.
    """

    output = {"asin": asin, "status": "pending", "submit_time": datetime.now()}

    if db.check_product(asin):
        output["status"] = "failed"
        output["error"] = "Product already exists in the database."
    else:
        db.db["submition"].insert_one(output)

    return output
