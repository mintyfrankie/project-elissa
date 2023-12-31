"""Some common functions for Selenium spiders."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def is_antirobot(driver: webdriver.Chrome) -> bool:
    """Check if the anti-robot page is displayed."""

    TITLE_1 = "nos excuses"
    TITLE_2 = "amazon.fr"
    title = driver.title.lower()
    if TITLE_1 in title or TITLE_2 == title:
        return True
    return False


def is_filtered(title: str, filter: set[str]) -> bool:
    """Check if the title contains any of the filter words."""

    return any(word.lower() in title.lower() for word in filter)


def CustomDriver() -> webdriver.Chrome:
    """Create a custom Chrome driver."""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--lang=fr")
    driver = webdriver.Chrome(options=options)
    return driver
