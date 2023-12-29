"""
A spider for scraping the search pages of the website.
"""

from datetime import datetime
from time import time
from types import SimpleNamespace
from urllib.parse import urlencode, urljoin

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.utils.common import is_antirobot
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

    return SearchItem(asin=asin, title=title, image=image)  # type: ignore


def get_nextpage(driver: webdriver.Chrome) -> str | None:
    """
    Turn the page.
    """
    try:
        next_button = driver.find_element(By.XPATH, Patterns.pagination_next)
        url = urljoin("https://www.amazon.fr", next_button.get_attribute("href"))
        return url
    except NoSuchElementException:
        return None


class SearchPageSpider:
    """A spider for scraping the search pages of the website."""

    def __init__(self, driver: webdriver.Chrome, keywords: set[str]) -> None:
        from mongodb.client import DatabaseClient

        self.driver = driver
        self.keywords = keywords
        self.urls = [
            "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            for keyword in keywords
        ]
        self.time = int(time())
        self.strtime = datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")
        self.asins = set()
        self.meta = {}
        self.data = []

        print("SearchPageSpider is initialized.")
        self.mongodb = DatabaseClient()
        self.session_id = self.mongodb.get_sessionid()
        assert self.mongodb.check_connection(), "Connection is not established."
        print("DatabaseClient is initialized.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mongodb.close()
        print("DatabaseClient is closed.")
        self.driver.close()
        self.driver.quit()
        print("SearchPageSpider is closed.")

    def parse(self, url: str) -> dict:
        """Parse a searching page."""

        self.driver.get(url)
        print(f"current_url: {self.driver.current_url}")

        if is_antirobot(self.driver):
            print("Anti-robot check is triggered.")
            return {}

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

        print(f"Scraped {len(items)} items.")
        next_page = get_nextpage(self.driver)

        return {"next_page": next_page, "items": items}

    def run(self) -> list[SearchItem]:
        """Run the spider."""

        def process_items(items):
            for item in items:
                if not self.mongodb.check_product(item["asin"]):
                    item["last_updated_id"] = self.session_id
                    item["last_updated_time"] = self.strtime
                    self.mongodb.update_product(item)
                    print(f"Updated {item['asin']}.")

        for url in self.urls:
            while url:
                output = self.parse(url)
                items = output["items"]
                process_items(items)
                self.data.extend(items)
                url = output.get("next_page")

        # Log the meta data.
        ACTION_TYPE = "search_page"
        item_count = len(self.data)

        self.meta["action_type"] = ACTION_TYPE
        self.meta["action_time"] = self.time
        self.meta["item_count"] = item_count
        self.meta["query_keywords"] = list(self.keywords)

        print(f"Scraped {item_count} items in total.")
        return self.data

    def log(self) -> dict:
        """Log the session activities to the database."""

        self.mongodb.log(self.meta)
        print("Session activities are logged.")
        return self.meta
