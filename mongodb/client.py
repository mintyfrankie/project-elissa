"""A client for MongoDB access."""


from datetime import datetime

import pandas as pd
from bson import json_util
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from .interfaces import DatabaseCounter, SessionLog, SessionLogInfo


def load_env_uri() -> str:
    """
    Retrieves the default MongoDB URI from the .env file.

    Returns:
        str: The default MongoDB URI.

    Raises:
        KeyError: If the MONGODB_URI is not set in the .env file.
    """

    from dotenv import dotenv_values

    try:
        config = dotenv_values(".env")
        return config["MONGODB_URI"]
    except KeyError:
        ERROR_MESSAGE = "Please set MONGODB_URI in .env file"
        raise KeyError(ERROR_MESSAGE)


class DatabaseClient:
    DB_NAME = "amazon"
    ITEM_COLLECTION_NAME = "items"
    LOG_COLLECTION_NAME = "session_logs"
    COUNTER_COLLECTION_NAME = "log_counters"

    def __init__(
        self,
        uri: str | None = None,
        action_type: str | None = "DatabaseClient: Default Action",
    ) -> None:
        """
        Initialize a MongoDB client.

        Args:
            uri (str | None): The MongoDB connection URI. If None, the default URI will be used.

        Returns:
            None
        """
        if uri is None:
            uri = load_env_uri()

        self.client = MongoClient(
            uri,
            server_api=ServerApi(version="1"),
        )
        self.db = self.client[self.DB_NAME]
        self.collection = self.db[self.ITEM_COLLECTION_NAME]
        self.log_collection = self.db[self.LOG_COLLECTION_NAME]
        self.counter_collection = self.db[self.COUNTER_COLLECTION_NAME]
        self.session_id = self.get_counter()
        self._logged = False
        self.action_type = action_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._logged:
            self.log(
                SessionLogInfo(
                    update_count=0, message="Session ended without inserting info."
                )
            )
        self.close()

    def close(self):
        """
        Closes the MongoDB client connection.
        """
        self.client.close()

    def check_connection(self) -> bool:
        """Check if the connection is established.

        Returns:
            bool: True if the connection is established, False otherwise.
        """
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_counter(self) -> int:
        """
        Retrieves the current counter value from the database; if the counter does not exist, it is created and set to 0.

        Returns:
            int: The current counter value.
        """
        doc = self.counter_collection.find_one({"_id": "log_counter"})
        if doc is None:
            INITIAL_COUNT = 0
            document = DatabaseCounter(count=INITIAL_COUNT)
            self.counter_collection.insert_one(document.__dict__)
            return INITIAL_COUNT
        else:
            return doc["count"]

    def increment_counter(self) -> None:
        """
        Increments the counter value by 1.
        """
        document = DatabaseCounter()
        self.counter_collection.update_one(
            document.get_id(), document.increment_count()
        )
        current_counter = self.get_counter()
        return current_counter

    def log(self, info: SessionLogInfo) -> SessionLog:
        """
        Logs the session information.

        Args:
            info (SessionLogInfo | dict): The session log information.

        Returns:
            SessionLog: The logged session information.
        """

        self.increment_counter()
        id = self.get_counter()
        content = SessionLog(
            id=id,
            time=datetime.now(),
            action_type=self.action_type,
            info=info,
        )
        self.log_collection.insert_one(content.model_dump())
        self._logged = True
        return content

    def check_product(self, asin: str) -> bool:
        """
        Check if a product with the given ASIN exists in the collection.

        Args:
            asin (str): The ASIN (Amazon Standard Identification Number) of the product.

        Returns:
            bool: True if a product with the given ASIN exists in the collection, False otherwise.
        """
        return self.collection.count_documents({"asin": asin}) > 0

    def find_product(self, asin: str) -> dict | None:
        """
        Find a product in the collection based on the given ASIN.

        Args:
            asin (str): The ASIN of the product to find.

        Returns:
            dict | None: A dictionary representing the found product, or None if not found.
        """
        return self.collection.find_one({"asin": asin})

    def get_asins(self) -> list[str]:
        """
        Retrieves a list of ASINs from the collection.

        Returns:
            list[str]: A list of ASINs.
        """

        return list(self.collection.distinct("asin"))

    def update_product(self, product: dict) -> bool:
        """
        Updates a product in the collection.

        Args:
            product: The product to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        result = self.collection.update_one(
            {"asin": product["asin"]},
            {"$set": product},
            upsert=True,
        )

        return result.acknowledged

    def snapshot(self, download_path: str | None = None) -> list[dict]:
        """
        Takes a snapshot of the collection and returns a list of documents.

        Args:
            download_path (str | None): Optional. The path to save the snapshot as a JSON file.

        Returns:
            list[dict]: A list of documents in the collection.
        """
        items = list(self.collection.find({}))
        if download_path is not None:
            with open(download_path, "w", encoding="utf-8") as f:
                f.write(json_util.dumps(items))
            print(f"Snapshot is saved to {download_path}.")
        return items

    def export_products(self) -> pd.DataFrame:
        from scraping.interfaces import ProductItem

        project = {key: 1 for key in ProductItem.model_fields.keys()}
        project["_id"] = 0

        EXCLUDED_KEYS = ["metadata", "review_url"]
        for key in EXCLUDED_KEYS:
            project.pop(key)

        products = list(self.collection.find({}, project))
        products = pd.DataFrame(products)
        print(f"Queried {len(products)} products.")

        return products

    def export_reviews(self) -> pd.DataFrame:
        project = {"_id": 0, "reviews": 1, "asin": 1}
        items = list(self.collection.find({}, project))

        def rowify_reviews(item):
            reviews = item["reviews"]
            asin = item["asin"]
            for review in reviews:
                review["asin"] = asin
                yield review

        items = [review for item in items for review in rowify_reviews(item)]
        reviews = pd.DataFrame(items)
        reviews = reviews[["asin"] + [col for col in reviews.columns if col != "asin"]]
        print(f"Queried {len(reviews)} reviews.")

        return reviews
