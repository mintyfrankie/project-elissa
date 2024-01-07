"""Some common functions for Selenium spiders."""

from typing import Literal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
BrowserType = Literal["Chrome", "Firefox", "Edge", "Safari"]


def get_driver(driver_type: BrowserType = "Chrome") -> SeleniumDriver:
    """Get a Selenium driver."""

    match driver_type:
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
