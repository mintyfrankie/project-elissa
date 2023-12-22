"""
A spider for scraping the search pages of the website.
"""

from types import SimpleNamespace

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.utils.items import SearchItem

Patterns = SimpleNamespace(
    main_frame=".//div[@data-component-type='s-search-result']",
    asins=".//div[@data-asin]",
    asin_title=".//h2/a/span",
    image_url=".//img[@class='s-image']",
    pagination_next=".//a[contains(@class, 's-pagination-next')]",
)


def get_main_frame(driver: webdriver.Chrome) -> WebElement | None:
    """Get the main frame of the search page."""

    try:
        return driver.find_element(By.XPATH, Patterns.main_frame)
    except NoSuchElementException:
        return None


def get_asin_cards(main_frame: WebElement) -> list[WebElement]:
    """Get the ASIN cards from the main frame."""

    return main_frame.find_elements(By.XPATH, Patterns.asins)


def parse_asin_cards(asin_card: WebElement) -> SearchItem:
    """Parse the ASIN cards."""

    asin = asin_card.get_attribute("data-asin")
    title = asin_card.find_element(By.XPATH, Patterns.asin_title).get_attribute(
        "textContent"
    )
    image = asin_card.find_element(By.XPATH, Patterns.image_url).get_attribute("src")

    return SearchItem(asin=asin, title=title, image=image)


def turn_page(driver: webdriver.Chrome) -> bool:
    """Turn the page."""

    try:
        next_page = driver.find_element(By.XPATH, Patterns.pagination_next)
        next_page.click()
        return True
    except NoSuchElementException:
        return False


# TODO: improve logic
class SearchPageSpider:
    """A spider for scraping the search pages of the website."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver

    def parse(self, url: str) -> list[SearchItem]:
        """Parse the search page."""

        self.driver.get(url)
        main_frame = get_main_frame(self.driver)
        if main_frame is None:
            return []
        asin_cards = get_asin_cards(main_frame)

        return [parse_asin_cards(asin_card) for asin_card in asin_cards]

    def turn_page(self) -> bool:
        """Turn the page."""

        return turn_page(self.driver)
