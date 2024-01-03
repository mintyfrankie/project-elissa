"""
Base class for all spiders
"""

from abc import ABC, abstractmethod
from .common import SeleniumDriver


class BaseItemScraper(ABC):
    """Base class for item scrapers.

    A ItemScraper is a worker for processing a single item-object.
    It can be search page of a keyword, a product page, or review pages of a product.
    """

    def __init__(self, driver: SeleniumDriver, starting_url: str) -> None:
        self.driver = driver
        self.__starting_url = starting_url
        self.__data = []

    @abstractmethod
    def parse(self) -> dict:
        """Parse a page and return the data."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """Run the scraper that can iterate over multiple pages."""
        raise NotImplementedError

    @abstractmethod
    def dump(self) -> list[dict]:
        """Dump the data."""
        raise NotImplementedError


class BaseSpider(ABC):
    """Base class for functional spiders.

    A Spider is a worker for processing a group of item-objects according to a specific action.
    It takes upon a queue of items, and process them one by one.
    It also takes care of the database connection.
    """

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str,
        queue: list[str] | None = None,
        pipeline: list[dict] | None = None,
    ) -> None:
        from mongodb.client import DatabaseClient

        self.driver = driver
        self.__queue = queue
        self.__piepline = pipeline
        self.__meta = {}

        self.mongodb = DatabaseClient(action_type=action_type)
        self.session_id = self.mongodb.session_id
        if not self.mongodb.check_connection():
            raise ConnectionError("Database connection failed.")
        print("DatabaseClient initialized with successful connection to MongoDB.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mongodb.close()
        print("DatabaseClient closed.")
        self.driver.quit()
        print("SeleniumDriver closed.")

    # TODO: metaprogramming - check how to interact with the BaseItemScraper
    @abstractmethod
    def process(self, item: str) -> None:
        """Process a single item."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """Run the spider."""
        raise NotImplementedError
