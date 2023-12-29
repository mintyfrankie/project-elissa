"""A test file for MongoDB access."""


import datetime

from dotenv import dotenv_values
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

config = dotenv_values(".env")


class DatabaseClient:
    """A class to upload data to MongoDB."""

    URI = config["MONGODB_URI"]
    DB_NAME = "amazon"
    ITEM_COLLECTION_NAME = "items"
    LOG_COLLECTION_NAME = "logs"
    COUNTER_COLLECTION_NAME = "log_counters"

    def __init__(self) -> None:
        self.client = MongoClient(
            self.URI,
            server_api=ServerApi(version="1"),
        )
        self.db = self.client[self.DB_NAME]
        self.collection = self.db[self.ITEM_COLLECTION_NAME]
        self.log_collection = self.db[self.LOG_COLLECTION_NAME]
        self.counter_collection = self.db[self.COUNTER_COLLECTION_NAME]

    def __close__(self) -> None:
        self.client.close()

    def check_connection(self) -> bool:
        """Check if the connection is established."""

        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def update_log_counter(self) -> int:
        """Update the log counter, and return the current count."""

        self.counter_collection.update_one(
            {"_id": "logid"},
            {"$inc": {"seq": 1}},
        )

        counter = self.counter_collection.find_one({"_id": "logid"})
        return counter["seq"]

    def log(self, message: str | None = None) -> int:
        """Create a log entry, and return the log id."""

        logid = self.update_log_counter()
        self.log_collection.insert_one(
            {
                "logid": logid,
                "time": datetime.datetime.now(datetime.UTC),
                "message": message,
            }
        )
        return logid

    def check_product(self, asin: str) -> bool:
        """Check if a product is in the database."""

        return self.collection.count_documents({"asin": asin}) > 0

    def update_product(self, product: dict) -> bool:
        """Update a product in the database."""

        result = self.collection.update_one(
            {"asin": product["asin"]},
            {"$set": product},
            upsert=True,
        )

        return result.acknowledged


if __name__ == "__main__":
    uploader = DatabaseClient()
    uploader.client.admin.command("ping")
    print("Connection is established.")
