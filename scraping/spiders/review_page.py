"""
A spider for scraping the review pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

PATTERNS = SimpleNamespace(
    review_card=".//div[@data-hook='review']",
    rating="//i[@data-hook='review-star-rating']//span",
    title="//a[@data-hook='review-title']//span[not(@class)]",
    metadata="//span[@data-hook='review-date']",
    body="//span[@data-hook='review-body']",
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
            metadata = metadata.split("le", maxsplit=1)
            if len(metadata) == 2:
                country = metadata[0].strip().replace("commenté", "")
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
