"""
Contains functions to parse the review page.
"""

import re
from datetime import datetime
from types import SimpleNamespace
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.common import SeleniumDriver

PATTERNS = SimpleNamespace(
    review_card="//div[@data-hook='review']",
    rating=".//i[@data-hook='review-star-rating' or @data-hook='cmps-review-star-rating']//span",
    title=".//a[@data-hook='review-title']//span[not(@class)]",
    title_2=".//span[@data-hook='review-title']/span[@class='cr-original-review-content']",
    metadata=".//span[@data-hook='review-date']",
    body=".//span[@data-hook='review-body']",
    next_page="//li[@class='a-last']//a[@href]",
)


def get_review_cards(driver: SeleniumDriver) -> list[WebElement]:
    """Get the review cards from the review page."""

    review_cards = driver.find_elements(By.XPATH, PATTERNS.review_card)
    return review_cards


def get_rating(review_card: WebElement) -> int | None:
    """Get the rating from a review card."""

    rating = review_card.find_elements(By.XPATH, PATTERNS.rating)
    if rating:
        rating = rating[0].get_attribute("textContent")
        if rating:
            rating = int(float(rating.split(" ", maxsplit=1)[0].replace(",", ".")))
            return rating
    return None


def get_title(review_card: WebElement) -> str | None:
    """Get the title from a review card."""

    title = review_card.find_elements(By.XPATH, PATTERNS.title)
    if title:
        title = title[0].get_attribute("textContent")
        return title

    title = review_card.find_elements(By.XPATH, PATTERNS.title_2)
    if title:
        title = title[0].get_attribute("textContent")
        return title

    return None


def get_metadata(review_card: WebElement) -> tuple[str, str] | None:
    """Get the metadata from a review card, parse it and return a tuple of country and date."""

    metadata = review_card.find_elements(By.XPATH, PATTERNS.metadata)
    if metadata:
        metadata = metadata[0].get_attribute("textContent")
        if metadata:
            metadata = re.split(r"\sle\s", metadata, maxsplit=1)
            if len(metadata) == 2:
                country = metadata[0]
                replacements = ["Évaluté", "Commenté", "en", "aux", "au", "à"]
                for x in replacements:
                    country = country.replace(x, " ").strip()
                date = metadata[1].strip()
                french_to_english_months = {
                    "janvier": "January",
                    "février": "February",
                    "mars": "March",
                    "avril": "April",
                    "mai": "May",
                    "juin": "June",
                    "juillet": "July",
                    "août": "August",
                    "septembre": "September",
                    "octobre": "October",
                    "novembre": "November",
                    "décembre": "December",
                }

                def convert_to_datetime(date_string):
                    for fr, en in french_to_english_months.items():
                        date_string = date_string.replace(fr, en)
                    return datetime.strptime(date_string, "%d %B %Y")

                date = convert_to_datetime(date)

            return country, date
    return None


def get_body(review_card: WebElement) -> str | None:
    """Get the body from a review card."""

    body = review_card.find_elements(By.XPATH, PATTERNS.body)
    if body:
        body = body[0].get_attribute("textContent")
        if body:
            body = body.strip()
            return body
    return None


def get_next_page(driver: SeleniumDriver) -> str | None:
    """Get the url of the next page of a review page."""

    next_page = driver.find_elements(By.XPATH, PATTERNS.next_page)
    if next_page:
        next_page = next_page[0].get_attribute("href")
        if next_page:
            url = urljoin("https://amazon.fr", next_page)
            return url
    return None
