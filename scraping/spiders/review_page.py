"""
A spider for scraping the review pages of the website.
"""

import random
import re
import time
from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.utils.items import ItemMetadata
from scraping.utils.spiders import BaseSpider

PATTERNS = SimpleNamespace(
    review_card="//div[@data-hook='review']",
    rating=".//i[@data-hook='review-star-rating']//span",
    title=".//a[@data-hook='review-title']//span[not(@class)]",
    metadata=".//span[@data-hook='review-date']",
    body=".//span[@data-hook='review-body']",
    next_page="//li[@class='a-last']//a[@href]",
)


def get_review_cards(driver: webdriver.Chrome) -> list[WebElement]:
    """
    Return the review cards.
    """

    review_cards = driver.find_elements(By.XPATH, PATTERNS.review_card)
    return review_cards


def get_rating(review_card: WebElement) -> int | None:
    """
    Return the rating of the review.
    """

    rating = review_card.find_elements(By.XPATH, PATTERNS.rating)
    if rating:
        rating = rating[0].get_attribute("textContent")
        if rating:
            rating = int(float(rating.split(" ", maxsplit=1)[0].replace(",", ".")))
            return rating
    return None


def get_title(review_card: WebElement) -> str | None:
    """
    Return the title of the review.
    """

    title = review_card.find_elements(By.XPATH, PATTERNS.title)
    if title:
        title = title[0].get_attribute("textContent")
        return title
    return None


def get_metadata(review_card: WebElement) -> tuple[str, str] | None:
    """
    Return the metadata of the review.
    """

    metadata = review_card.find_elements(By.XPATH, PATTERNS.metadata)
    if metadata:
        metadata = metadata[0].get_attribute("textContent")
        if metadata:
            metadata = re.split(r"\sle\s", metadata, maxsplit=1)
            if len(metadata) == 2:
                country = metadata[0].replace("Commenté", "").strip()
                date = metadata[1].strip()
                return country, date
    return None


def get_body(review_card: WebElement) -> str | None:
    """
    Return the body of the review.
    """

    body = review_card.find_elements(By.XPATH, PATTERNS.body)
    if body:
        body = body[0].get_attribute("textContent")
        if body:
            body = body.strip()
            return body
    return None


def get_next_page(driver: webdriver.Chrome) -> str | None:
    """
    Return the next page.
    """

    next_page = driver.find_elements(By.XPATH, PATTERNS.next_page)
    if next_page:
        next_page = next_page[0].get_attribute("href")
        if next_page:
            url = urljoin("https://amazon.fr", next_page)
            return url
    return None


class ReviewPageSpider(BaseSpider):
    """
    A spider for scraping the review pages of the website.
    """

    default_pipeline = [
        {"$match": {"_metadata.review_page_scraped": False}},
        {"$project": {"asin": 1, "review_url": 1, "_id": 0}},
    ]

    def __init__(self, driver: webdriver.Chrome) -> None:
        super().__init__(driver)
        self.queue = []

    def query(self, pipeline: list[dict] = default_pipeline) -> list[dict]:
        """
        Get the products to scrape.
        """

        items = list(self.mongodb.collection.aggregate(pipeline))
        self.queue = items
        print(f"Found {len(items)} products to scrape.")
        return items

    def parse(self, url: str) -> dict:
        """
        Parse a review page of a product.
        """

        self.driver.get(url)

        review_cards = get_review_cards(self.driver)
        next_page = get_next_page(self.driver)
        reviews = []
        if review_cards:
            for review_card in review_cards:
                review = {}
                metadata = get_metadata(review_card)
                review["rating"] = get_rating(review_card)
                review["title"] = get_title(review_card)
                review["country"] = None
                review["date"] = None
                review["body"] = get_body(review_card)
                if metadata:
                    review["country"], review["date"] = metadata
                reviews.append(review)

        # Random sleep.
        time.sleep(random.uniform(0.5, 1.5))

        return {"reviews": reviews, "next_page": next_page}

    def run(self, max_page: int = 10) -> None:
        """
        Run the spider.
        """

        if not self.queue:
            raise ValueError("No products to scrape, run query() first.")

        def process_item(product: dict) -> int:
            """Process the item."""

            asin = product["asin"]
            review_url = product["review_url"]

            reviews = []
            page_count = 0
            while review_url and page_count < max_page:
                output = self.parse(review_url)
                reviews += output["reviews"]
                review_url = output["next_page"]
                page_count += 1
                print(f"Scrapping {asin} --- Page {page_count}/{max_page}")

            metadata: ItemMetadata = {
                "last_session_id": self.session_id,
                "last_session_time": self.strtime,
                "product_page_scraped": True,
                "review_page_scraped": True,
            }
            product["_metadata"] = metadata
            product["reviews"] = reviews

            self.mongodb.collection.update_one(
                {"asin": asin},
                {"$set": product},
            )

            print(f"Scraped {asin}.")
            return 1

        counter = 0
        for product in self.queue:
            asin = product["asin"]
            counter += process_item(product)
            print(
                f"Updated {asin} ------------------- Progress {counter}/{len(self.queue)}"
            )

        # Log the session.
        ACTION_TYPE = "Review Page Scraping"

        self.meta["action_type"] = ACTION_TYPE
        self.meta["action_time"] = self.time
        self.meta["update_count"] = counter

        print(f"Scraped {counter} products.")
        self.log()
