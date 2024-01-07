"""
A spider for scraping the review pages of the website.
"""

import re
from datetime import datetime
from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from mongodb.interfaces import SessionLogInfo
from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import SeleniumDriver, is_antirobot
from scraping.interfaces import ItemMetadata

PATTERNS = SimpleNamespace(
    review_card="//div[@data-hook='review']",
    rating=".//i[@data-hook='review-star-rating' or @data-hook='cmps-review-star-rating']//span",
    title=".//a[@data-hook='review-title']//span[not(@class)]",
    title_2=".//span[@data-hook='review-title']/span[@class='cr-original-review-content']",
    metadata=".//span[@data-hook='review-date']",
    body=".//span[@data-hook='review-body']",
    next_page="//li[@class='a-last']//a[@href]",
)


def get_review_cards(driver: webdriver.Chrome) -> list[WebElement]:
    """
    Return the review cards.
    """

    review_cards = driver.find_elements(By.XPATH, PATTERNS.review_card)
    return review_cards


def get_rating(review_card: WebElement) -> int | None:
    """
    Return the rating of the review.
    """

    rating = review_card.find_elements(By.XPATH, PATTERNS.rating)
    if rating:
        rating = rating[0].get_attribute("textContent")
        if rating:
            rating = int(float(rating.split(" ", maxsplit=1)[0].replace(",", ".")))
            return rating
    return None


def get_title(review_card: WebElement) -> str | None:
    """
    Return the title of the review.
    """

    title = review_card.find_elements(By.XPATH, PATTERNS.title)
    if title:
        title = title[0].get_attribute("textContent")
        return title

    title = review_card.find_elements(By.XPATH, PATTERNS.title_2)
    if title:
        title = title[0].get_attribute("textContent")
        return title

    return None


def get_metadata(review_card: WebElement) -> tuple[str, str] | None:
    """
    Return the metadata of the review.
    """

    metadata = review_card.find_elements(By.XPATH, PATTERNS.metadata)
    if metadata:
        metadata = metadata[0].get_attribute("textContent")
        if metadata:
            metadata = re.split(r"\sle\s", metadata, maxsplit=1)
            if len(metadata) == 2:
                country = metadata[0]
                replacements = ["Évaluté", "Commenté", "en", "aux", "au", "à"]
                for x in replacements:
                    country = country.replace(x, " ").strip()
                date = metadata[1].strip()
                french_to_english_months = {
                    "janvier": "January",
                    "février": "February",
                    "mars": "March",
                    "avril": "April",
                    "mai": "May",
                    "juin": "June",
                    "juillet": "July",
                    "août": "August",
                    "septembre": "September",
                    "octobre": "October",
                    "novembre": "November",
                    "décembre": "December",
                }

                def convert_to_datetime(date_string):
                    for fr, en in french_to_english_months.items():
                        date_string = date_string.replace(fr, en)
                    return datetime.strptime(date_string, "%d %B %Y")

                date = convert_to_datetime(date)

            return country, date
    return None


def get_body(review_card: WebElement) -> str | None:
    """
    Return the body of the review.
    """

    body = review_card.find_elements(By.XPATH, PATTERNS.body)
    if body:
        body = body[0].get_attribute("textContent")
        if body:
            body = body.strip()
            return body
    return None


def get_next_page(driver: webdriver.Chrome) -> str | None:
    """
    Return the next page.
    """

    next_page = driver.find_elements(By.XPATH, PATTERNS.next_page)
    if next_page:
        next_page = next_page[0].get_attribute("href")
        if next_page:
            url = urljoin("https://amazon.fr", next_page)
            return url
    return None


class ReviewItemScraper(BaseItemScraper):
    """A scraper for scraping all review pages for an ASIN."""

    def __init__(
        self, driver: SeleniumDriver, starting_url: str, max_page: int = -1
    ) -> None:
        super().__init__(driver, starting_url)
        self._max_page = max_page

    def parse(self, url: str) -> dict[str, list[str]]:
        """
        Parse the review page and extracts relevant information.

        Returns:
           dict: A dictionary containing the next page URL and a list of items.
        """

        self.driver.get(url)
        print(f"##### Parsing URL: {url}")

        if is_antirobot(self.driver):
            return {}

        review_cards = get_review_cards(self.driver)
        next_page = get_next_page(self.driver)
        items = []
        if review_cards:
            for review_card in review_cards:
                item = {}
                metadata = get_metadata(review_card)
                item["rating"] = get_rating(review_card)
                item["title"] = get_title(review_card)
                item["country"] = None
                item["date"] = None
                item["body"] = get_body(review_card)
                if metadata:
                    item["country"], item["date"] = metadata
                items.append(item)

        return {"next_page": next_page, "items": items}

    def run(self) -> None:
        """
        Executes the spider and collects data from the starting URL and subsequent pages.

        Returns:
            None
        """

        url = self._starting_url
        page_count = 0
        while url and (self._max_page == -1 or page_count < self._max_page):
            output = self.parse(url)
            items = output.get("items")
            self._data.extend(items) if items else None
            url = output.get("next_page")
            page_count += 1

    def validate(self) -> bool:
        """
        Validates the data.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
        return True

    def dump(self) -> list[dict]:
        """
        Returns the data stored in the object as a list of dictionaries.

        Returns:
            list[dict]: The data stored in the object.
        """
        return self._data


class ReviewPageSpiderWorker(BaseSpiderWorker):
    """
    Spider worker class for scraping review pages.

    This class extends the BaseSpiderWorker class and provides methods for querying the database,
    scraping review pages, updating the database, and logging metadata.

    Attributes:
        DEFAULT_PIPELINE (list[dict]): The default pipeline used for querying the database.
        _pipeline (list[dict]): The pipeline used for querying the database.
        _queue (list): The list of ASINs to be processed.
        _data (list): The list of scraped review items.
        __kwargs (dict): Additional keyword arguments.

    Methods:
        __init__: Initializes the ReviewPageSpiderWorker object.
        query: Queries the database collection and retrieves a list of ASINs.
        run: Runs the review page scraping process.
        log: Logs the metadata.
    """

    DEFAULT_PIPELINE = [
        {
            "$match": {
                "$and": [
                    {"_metadata.scrap_status": "ProductPage"},
                ]
            }
        },
        {"$project": {"asin": 1, "_id": 0, "review_url": 1}},
    ]

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str = "Review Page Scraping",
        pipeline: list[dict] | None = None,
        **kwargs,
    ) -> None:
        """
        Initializes the ReviewPageSpiderWorker object.

        Args:
            driver (SeleniumDriver): The Selenium driver object.
            action_type (str): The type of action being performed.
            pipeline (list[dict] | None): The pipeline used for querying the database.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(driver, action_type)
        self._pipeline = pipeline or self.DEFAULT_PIPELINE
        self.__kwargs = kwargs

    def query(self) -> None:
        """
        Queries the database collection and retrieves a list of ASINs.
        """
        asins = list(self.db.collection.aggregate(self._pipeline))
        self._queue = asins

    def run(self) -> None:
        """
        Runs the review page scraping process.
        """

        self.query()
        if self._pipeline == self.DEFAULT_PIPELINE:
            print("Use default pipeline to query the database.")
        print(f"Found {len(self._queue)} items to update.")

        for elem in self._queue:
            asin = elem.get("asin")
            url = elem.get("review_url")
            scraper = ReviewItemScraper(self.driver, url, **self.__kwargs)
            scraper.run()
            items = scraper.dump()
            elem["reviews"] = items
            # add metadata
            metadata = ItemMetadata(
                last_session_id=self.session_id,
                last_session_time=self._init_time,
                scrap_status="ReviewPage",
            )
            elem["_metadata"] = dict(metadata)

            self._data.extend(elem)
            self.db.update_product(elem)
            print(f"Updated {asin} -- Progress {len(self._data)}/{len(self._queue)}")

        print(f"Updated {len(self._data)} items in total.")

    def log(self) -> dict:
        """
        Logs the metadata.

        This method logs the metadata by adding the action time and update count to the meta dictionary.
        It then calls the `log` method of the `db` object to store the metadata in the database.

        Returns:
            dict: The updated meta dictionary.
        """
        self._meta["update_count"] = len(self._data)
        self._meta["updated_asins"] = list(self._queue)
        info = SessionLogInfo(**self._meta)
        self.db.log(info)
        return self._meta
