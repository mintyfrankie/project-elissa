from types import SimpleNamespace
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.common import SeleniumDriver

PATTERNS = SimpleNamespace(
    main_frame="//span[@data-component-type='s-search-results']",
    asins="//div[@data-asin]",
    asin_title=".//h2/a/span",
    image_url=".//img[@class='s-image']",
    pagination_next=".//a[contains(@class, 's-pagination-next')]",
)


def get_mainframe(driver: SeleniumDriver) -> WebElement | None:
    try:
        return driver.find_element(By.XPATH, PATTERNS.main_frame)
    except NoSuchElementException:
        return None


def get_asin_cards(main_frame: WebElement) -> list[WebElement]:
    return main_frame.find_elements(By.XPATH, PATTERNS.asins)


def parse_asin_card(asin_card: WebElement) -> dict:
    asin = asin_card.get_attribute("data-asin")
    if not asin:
        asin = ""
    try:
        title = asin_card.find_element(By.XPATH, PATTERNS.asin_title).get_attribute(
            "textContent"
        )
    except NoSuchElementException:
        title = ""

    try:
        image = asin_card.find_element(By.XPATH, PATTERNS.image_url).get_attribute(
            "src"
        )
    except NoSuchElementException:
        image = None

    output = {
        "asin": asin,
        "title": title,
        "thumbnail": image,
    }

    return output


def get_nextpage(driver: SeleniumDriver) -> str | None:
    try:
        next_button = driver.find_element(By.XPATH, PATTERNS.pagination_next)
        url = urljoin("https://www.amazon.fr", next_button.get_attribute("href"))
        return url
    except NoSuchElementException:
        return None
