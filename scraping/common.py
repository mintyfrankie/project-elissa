"""Some common functions for Selenium spiders."""

from typing import Literal

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DEFAULT_BROWSER_TYPE = "Chrome"

QUERY_KEYWORDS = {
    "serviette femme",
    "tampon femme",
    "cup menstruelle",
    "protege slip",
    # "culotte menstruelle",
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


type SeleniumDriver = (
    webdriver.Chrome | webdriver.Firefox | webdriver.Edge | webdriver.Safari
)
BrowserType = Literal["Chrome", "Firefox", "Edge", "Safari", "Undetected"]


def get_driver(driver_type: BrowserType = DEFAULT_BROWSER_TYPE) -> SeleniumDriver:
    """Get a Selenium driver."""

    match driver_type:
        case "Undected":
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


def random_sleep(min: float = 0.3, max: float = 1.5, message: bool = True) -> float:
    """Sleep for a random time between min and max seconds."""

    import random
    import time

    sec = random.uniform(min, max)
    time.sleep(sec)
    if message:
        print(f"Sleeping for {sec:.2f} seconds.")
    return sec
