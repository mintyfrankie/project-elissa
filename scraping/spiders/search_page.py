"""
A spider for scraping the search pages of the website.
"""

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

    return SearchItem(asin=asin, title=title, image=image)


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
        self.driver = driver
        self.keywords = keywords
        self.urls = [
            "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            for keyword in keywords
        ]
        self.time = int(time())
        self.asins = set()
        self.data = []

        print("SearchPageSpider is initialized.")

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

        for url in self.urls:
            output = self.parse(url)
            self.data += output["items"]
            while output["next_page"] is not None:
                output = self.parse(output["next_page"])
                self.data += output["items"]

        print(f"Scraped {len(self.data)} items in total.")
        return self.data

    def persist(self) -> dict:
        """Persist the data to the database."""

        output = {}
        output["time"] = self.time
        output["query_keywords"] = self.keywords
        output["item_count"] = len(self.data)
        output["data"] = self.data

        return output
