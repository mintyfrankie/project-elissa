"""
A spider for scraping the search pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urlencode, urljoin

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.utils.common import is_antirobot
from scraping.utils.items import SearchItem
from scraping.utils.spiders import BaseSpider

PATTERNS = SimpleNamespace(
    main_frame="//span[@data-component-type='s-search-results']",
    asins="//div[@data-asin]",
    asin_title=".//h2/a/span",
    image_url=".//img[@class='s-image']",
    pagination_next=".//a[contains(@class, 's-pagination-next')]",
)


def get_mainframe(driver: webdriver.Chrome) -> WebElement | None:
    """Get the main frame of the search page."""

    try:
        return driver.find_element(By.XPATH, PATTERNS.main_frame)
    except NoSuchElementException:
        return None


def get_asin_cards(main_frame: WebElement) -> list[WebElement]:
    """Get the ASIN cards from the main frame."""

    return main_frame.find_elements(By.XPATH, PATTERNS.asins)


def parse_asin_card(asin_card: WebElement) -> SearchItem:
    """Parse the ASIN cards."""

    asin = asin_card.get_attribute("data-asin")
    try:
        title = asin_card.find_element(By.XPATH, PATTERNS.asin_title).get_attribute(
            "textContent"
        )
    except NoSuchElementException:
        title = None

    try:
        image = asin_card.find_element(By.XPATH, PATTERNS.image_url).get_attribute(
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
        next_button = driver.find_element(By.XPATH, PATTERNS.pagination_next)
        url = urljoin("https://www.amazon.fr", next_button.get_attribute("href"))
        return url
    except NoSuchElementException:
        return None


class SearchPageSpider(BaseSpider):
    """A spider for scraping the search pages of the website."""

    def __init__(self, driver: webdriver.Chrome, keywords: set[str]) -> None:
        super().__init__(driver, keywords)

        self.urls = [
            "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            for keyword in keywords
        ]
        self.asins = set()
        self.meta = {}
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
            if item["asin"] not in self.asins and item["asin"] != "":
                self.asins.add(item["asin"])
                items.append(item)

        print(f"Scraped {len(items)} items.")
        next_page = get_nextpage(self.driver)

        return {"next_page": next_page, "items": items}

    def run(self) -> list[SearchItem]:
        """
        Run the spider.

        The spider will scrape the search pages for the given keywords, collecting all ASINs on the pages.
        If the scraped ASIN is not in the database, the spider will create a new document for it.
        """

        def process_item(item: SearchItem):
            """Process the item."""
            if not self.mongodb.check_product(item["asin"]):
                item["metadata"] = {}
                item["metadata"]["last_session_id"] = self.session_id
                item["metadata"]["last_session_time"] = self.strtime
                item["metadata"]["product_page_scraped"] = False
                self.mongodb.update_product(item)
                print(f"Updated {item['asin']}.")
                return 1
            else:
                print(f"{item['asin']} is already in the database.")
                return 0

        counter = 0
        for url in self.urls:
            while url:
                output = self.parse(url)
                items = output["items"]
                for item in items:
                    counter += process_item(item)
                self.data.extend(items)
                url = output.get("next_page")

        # Log the meta data.
        ACTION_TYPE = "Search Page Scraping"
        item_count = len(self.data)

        self.meta["action_type"] = ACTION_TYPE
        self.meta["action_time"] = self.time
        self.meta["update_count"] = counter
        self.meta["query_keywords"] = list(self.keywords)

        print(f"Scraped {item_count} items in total, {counter} items are new.")
        return self.data
