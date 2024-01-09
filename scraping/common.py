"""
Contain some common functions and constants for scraping.
"""

import random
import time
from typing import Literal

import undetected_chromedriver as uc
from amazoncaptcha import AmazonCaptcha
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SeleniumDriver = (
    webdriver.Chrome | webdriver.Firefox | webdriver.Edge | webdriver.Safari
)
BrowserType = Literal["Chrome", "Firefox", "Edge", "Safari", "Undetected"]


DEFAULT_BROWSER_TYPE = "Undetected"

QUERY_KEYWORDS = {
    "serviette hygiénique",
    "tampon femme",
    "cup menstruelle",
    "protege slip",
}

EXCLUDE_KEYWORDS = {
    "cheveux",
    "sport",
    "rangement",
    "bain",
    "microfibre",
    "douche",
    "maquillage",
    "plage",
    "décoration",
    "percer",
    "manucure",
    "pédicure",
    "trouse",
    "stérilisateur",
    "cuisine",
    "éponge",
    "épilation",
    "épilateur",
}


def is_antirobot(driver: SeleniumDriver) -> bool:
    """Check if the `Nos Excuses` blocking page is displayed."""

    EXCUSE_TITLE = "nos excuses"
    title = driver.title.lower()
    if EXCUSE_TITLE == title:
        return True
    return False


def is_captcha(driver: SeleniumDriver) -> bool:
    """Check if the captcha is displayed."""

    form_element = driver.find_elements(
        By.XPATH, "//form[@action='/errors/validateCaptcha']"
    )
    if form_element:
        return True
    return False


def solve_captcha(driver: SeleniumDriver) -> bool:
    """Solve the captcha using AmazonCaptcha."""

    form_element = driver.find_element(
        By.XPATH, "//form[@action='/errors/validateCaptcha']"
    )
    captcha_url = form_element.find_element(By.XPATH, "//img").get_attribute("src")
    captcha = AmazonCaptcha.fromlink(captcha_url)
    solution = captcha.solve()

    input_field = form_element.find_element(By.ID, "captchacharacters")
    input_field.send_keys(solution)

    submit_button = form_element.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()

    if is_captcha(driver):
        return False
    return True


def is_filtered(title: str, filter_set: set[str]) -> bool:
    """Check if the title contains any of the filter words."""

    return any(word.lower() in title.lower() for word in filter_set)


def get_driver(driver_type: BrowserType = DEFAULT_BROWSER_TYPE) -> SeleniumDriver:
    """Get a Selenium driver."""

    match driver_type:
        case "Undetected":
            driver = uc.Chrome()
        case "Chrome":
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--lang=fr")
            driver = webdriver.Chrome(options=options)
        case "Firefox":
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--lang=fr")
            driver = webdriver.Firefox(options=options)
        case "Edge":
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--lang=fr")
            driver = webdriver.Edge(options=options)
        case "Safari":
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--lang=fr")
            driver = webdriver.Safari(options=options)
        case _:
            raise ValueError("Invalid driver type.")
    return driver


def random_sleep(
    min_time: float = 0.3, max_time: float = 1.5, message: bool = True
) -> float:
    """Sleep for a random time between min and max seconds."""

    sec = random.uniform(min_time, max_time)
    time.sleep(sec)
    if message:
        print(f"Sleeping for {sec:.2f} seconds.")
    return sec
