"""
Contains the main function for the API.
"""

import pandas as pd
from fastapi import FastAPI

app = FastAPI()
products = pd.read_csv("./data/products.csv")
reviews = pd.read_csv("./data/reviews_en.csv")
scores = pd.read_csv("./data/scores.csv")


@app.get("/api/product/all")
async def get_all_product_asins():
    """
    Get all ASINs from the product table.
    """
    return products["asin"].tolist()


@app.get("/api/product/{asin}")
async def query_product(asin: str):
    """
    Query the product table for the given ASIN.
    """
    product = products[products["asin"] == asin]
    if product.empty:
        return None
    return product.iloc[0].to_dict()


@app.get("/api/product/search")
async def search_product():
    pass


@app.get("/api/scrape/product/{asin}")
# add authentication
async def scrape_product(asin: str):
    pass


@app.get("/api/scrape/review/{asin}")
# add authentication
def scrape_review(asin: str):
    pass


@app.post("/api/submit/product/{asin}")
# add authentication
def submit_product(asin: str):
    pass
