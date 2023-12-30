from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from mongodb.client import DatabaseClient
from scraping.spiders.product_page import ProductPageSpider
from scraping.spiders.review_page import ReviewPageSpider
from scraping.spiders.search_page import SearchPageSpider
from scraping.utils.constants import QUERY_KEYWORDS

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


def scrape_search_page():
    with SearchPageSpider(driver, QUERY_KEYWORDS) as spider:
        spider.run()


def scrape_product_page():
    with ProductPageSpider(driver) as spider:
        spider.run()


def scrape_review_page():
    with ReviewPageSpider(driver) as spider:
        spider.run(max_page=10)


def save_collection():
    with DatabaseClient() as db_client:
        db_client.snapshot(download_path="./data/snapshot.json")


if __name__ == "__main__":
    # scrape_search_page()
    # scrape_product_page()
    # scrape_review_page()
    save_collection()
