"""Some common functions for Selenium spiders."""

from selenium import webdriver


def is_antirobot(driver: webdriver.Chrome) -> bool:
    """Check if the anti-robot page is displayed."""

    return "nos excuses" in driver.title.lower()
