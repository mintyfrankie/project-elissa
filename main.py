from mongodb.client import DatabaseClient
from scraping.common import QUERY_KEYWORDS, get_driver
from scraping.spiders.product_page import ProductPageSpider
from scraping.spiders.review_page import ReviewPageSpider
from scraping.spiders.search_page import SearchPageSpiderWorker

driver = get_driver()


def scrape_search_page():
    with SearchPageSpiderWorker(driver, queue=QUERY_KEYWORDS) as spider:
        spider.run()


def scrape_product_page():
    with ProductPageSpider(driver) as spider:
        spider.query()
        spider.run()


def scrape_review_page():
    with ReviewPageSpider(driver) as spider:
        pipeline = [
            {"$match": {}},
            {"$project": {"asin": 1, "review_url": 1, "_id": 0}},
        ]
        spider.query(pipeline)
        spider.run(max_page=20)


def save_collection():
    with DatabaseClient() as db_client:
        db_client.snapshot(download_path="./data/snapshot.json")


if __name__ == "__main__":
    scrape_search_page()
    # scrape_product_page()
    # scrape_review_page()
    # save_collection()
