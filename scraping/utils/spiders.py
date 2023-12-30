"""
Base class for all spiders
"""

from datetime import datetime
from time import time

from selenium import webdriver


class BaseSpider:
    """A base spider class."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        from mongodb.client import DatabaseClient

        self.driver = driver
        self.time = int(time())
        self.strtime = datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")
        self.meta = {}

        self.mongodb = DatabaseClient()
        self.session_id = self.mongodb.session_id
        assert self.mongodb.check_connection(), "Connection is not established."
        print("DatabaseClient initialized with successful connection to MongoDB.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mongodb.close()
        print("DatabaseClient is closed.")
        self.driver.close()
        self.driver.quit()
        print("SearchPageSpider is closed.")

    def parse(self, url: str) -> dict:
        """Parse a page."""

        raise NotImplementedError

    def run(self) -> None:
        """Run the spider."""

        raise NotImplementedError

    def log(self) -> dict:
        """Log the session activities to the database."""

        assert self.meta != {}, "No session activities to log."
        self.mongodb.log(self.meta)
        print("Session activities are logged.")
        return self.meta
