"""
A spider for scraping the search pages of the website.
"""

from types import SimpleNamespace

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


Patterns = SimpleNamespace(
    main_frame=".//div[@data-component-type='s-search-result']",
    asins=".//div[@data-asin]",
    asin_title=".//h2/a/span",
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
