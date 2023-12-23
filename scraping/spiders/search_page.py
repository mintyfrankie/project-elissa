"""
A spider for scraping the search pages of the website.
"""

from time import time
from types import SimpleNamespace
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.utils.items import SearchItem

Patterns = SimpleNamespace(
    main_frame="//span[@data-component-type='s-search-results']",
    asins="//div[@data-asin]",
    asin_title=".//h2/a/span",
    image_url=".//img[@class='s-image']",
    pagination_next=".//a[contains(@class, 's-pagination-next')]",
)


def get_mainframe(driver: webdriver.Chrome) -> WebElement | None:
    """Get the main frame of the search page."""

    try:
        return driver.find_element(By.XPATH, Patterns.main_frame)
    except NoSuchElementException:
        return None


def get_asin_cards(main_frame: WebElement) -> list[WebElement]:
    """Get the ASIN cards from the main frame."""

    return main_frame.find_elements(By.XPATH, Patterns.asins)


def parse_asin_card(asin_card: WebElement) -> SearchItem:
    """Parse the ASIN cards."""

    asin = asin_card.get_attribute("data-asin")
    try:
        title = asin_card.find_element(By.XPATH, Patterns.asin_title).get_attribute(
            "textContent"
        )
    except NoSuchElementException:
        title = None

    try:
        image = asin_card.find_element(By.XPATH, Patterns.image_url).get_attribute(
            "src"
        )
    except NoSuchElementException:
        image = None

    return SearchItem(asin=asin, title=title, image=image)


def turn_page(driver: webdriver.Chrome) -> bool:
    """Turn the page."""

    try:
        next_page = driver.find_element(By.XPATH, Patterns.pagination_next)
        next_page.click()
        return True
    except NoSuchElementException:
        return False


class SearchPageSpider:
    """A spider for scraping the search pages of the website."""

    def __init__(self, driver: webdriver.Chrome, keywords: list[str]) -> None:
        self.driver = driver
        self.keywords = keywords
        self.urls = [
            "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            for keyword in keywords
        ]
        self.time = int(time())
        self.asins = set()
        self.data = []

    def parse(self, url: str) -> dict:
        """Parse a searching page."""

        self.driver.get(url)
        items = []

        main_frame = get_mainframe(self.driver)

        if main_frame == [] or main_frame is None:
            return {}

        asin_cards = get_asin_cards(main_frame)

        for asin_card in asin_cards:
            item = parse_asin_card(asin_card)
            if item["asin"] not in self.asins:
                self.asins.add(item["asin"])
                items.append(item)

        next_page = turn_page(self.driver)

        # FIXME: no items are found on every page
        return {"next_page": next_page, "items": self.data}

    def run(self) -> list:
        """Run the spider."""

        for url in self.urls:
            output = self.parse(url)
            self.data += output["items"]
            while output["next_page"]:
                output = self.parse(url)
                self.data += output["items"]

        return self.data

    def persist(self) -> dict:
        """Persist the data to the database."""

        output = {}
        output["time"] = self.time
        output["query_keywords"] = self.keywords
        output["item_count"] = len(self.data)
        output["data"] = self.data

        return output
