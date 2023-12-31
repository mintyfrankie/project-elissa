"""
Contain a list of default pipelines of SpiderWorkers to query the Database. 
"""

DEFAULT_PRODUCT_PAGE_PIPELINE = [
    {
        "$match": {
            "$and": [
                {"_metadata.scrap_status": "SearchPage"},
            ]
        }
    },
    {"$project": {"asin": 1, "_id": 0}},
]

DEFAULT_REVIEW_PAGE_PIPELINE = [
    {
        "$match": {
            "$and": [
                {"_metadata.scrap_status": "ProductPage"},
            ]
        }
    },
    {"$project": {"asin": 1, "_id": 0, "review_url": 1}},
]
