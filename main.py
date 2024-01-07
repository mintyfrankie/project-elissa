from scraping import (
    ProductPageSpiderWorker,
    ReviewPageSpiderWorker,
    SearchPageSpiderWorker,
    get_driver,
)
from scraping.common import QUERY_KEYWORDS

driver = get_driver("Chrome")


def scrape_search_page():
    with SearchPageSpiderWorker(driver=driver, queue=QUERY_KEYWORDS) as worker:
        worker.run()


def scrape_product_page():
    with ProductPageSpiderWorker(driver=driver) as worker:
        worker.run()


def scrape_review_page():
    with ReviewPageSpiderWorker(driver=driver) as worker:
        worker.run()


if __name__ == "__main__":
    scrape_search_page()
    # scrape_product_page()
    # scrape_review_page()
