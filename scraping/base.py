"""
Base class for all spiders
"""

from abc import ABC, abstractmethod
from datetime import datetime

from .common import SeleniumDriver


class BaseItemScraper(ABC):
    """Base class for item scrapers.

    A ItemScraper is a worker for processing a single item-object.
    It can be search page of a keyword, a product page, or review pages of a product.
    """

    def __init__(self, driver: SeleniumDriver, starting_url: str) -> None:
        self.driver = driver
        self._starting_url = starting_url
        self._data = []

    @abstractmethod
    def parse(self) -> dict:
        """Parse a page and return the data."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """Run the scraper that can iterate over multiple pages."""
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        """Validate the data."""
        raise NotImplementedError

    @abstractmethod
    def dump(self) -> list[dict]:
        """Dump the data."""
        raise NotImplementedError


class BaseSpiderWorker(ABC):
    """Base class for functional spiders.

    A Spider is a worker for processing a group of item-objects according to a specific action.
    It takes upon a queue of items, and process them one by one.
    It also takes care of the database connection.
    """

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str,
    ) -> None:
        from mongodb.client import DatabaseClient

        self.driver = driver
        self.db = DatabaseClient(action_type=action_type)
        self._data = []
        self._meta = {}
        self._logged = False
        self._init_time = datetime.now()

        self.session_id = self.db.session_id
        if not self.db.check_connection():
            raise ConnectionError("Database connection failed.")
        print("DatabaseClient initialized with successful connection to MongoDB.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._logged:
            self.log()
        self.db.close()
        print("DatabaseClient closed.")
        self.driver.quit()
        print("SeleniumDriver closed.")

    @abstractmethod
    def query(self) -> None:
        """Query the database for constructing the queue used in run()."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """
        Run the spider.

        The spider should iterate over the queue and process each item.
        """
        raise NotImplementedError

    @abstractmethod
    def log(self) -> None:
        """Log the data."""
        raise NotImplementedError
