"""Some common functions for Selenium spiders."""

from selenium import webdriver


def is_antirobot(driver: webdriver.Chrome) -> bool:
    """Check if the anti-robot page is displayed."""

    return "nos excuses" in driver.title.lower()


def is_filtered(title: str, filter: set[str]) -> bool:
    """Check if the title contains any of the filter words."""

    return any(word.lower() in title.lower() for word in filter)
