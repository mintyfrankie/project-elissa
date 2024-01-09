"""
Contains the main function to run the scraping.
"""

from scraping import (
    ProductPageSpiderWorker,
    ReviewPageSpiderWorker,
    SearchPageSpiderWorker,
    get_driver,
)

driver = get_driver("Chrome")


def scrape_search_page():
    """Scrape the search pages."""

    with SearchPageSpiderWorker(driver=driver) as worker:
        worker.run()


def scrape_product_page():
    """Scrape the product pages."""

    with ProductPageSpiderWorker(driver=driver) as worker:
        worker.run()


def scrape_review_page():
    """Scrape the review pages."""

    with ReviewPageSpiderWorker(driver=driver) as worker:
        worker.run()


if __name__ == "__main__":
    # scrape_search_page()
    # scrape_product_page()
    # scrape_review_page()
