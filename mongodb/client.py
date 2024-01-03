"""A client for MongoDB access."""


import datetime

from bson import json_util
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from scraping.utils.items import SearchItem, SessionLog, SessionLogInfo


class DatabaseClient:
    """A class to upload data to MongoDB."""

    DB_NAME = "amazon"
    ITEM_COLLECTION_NAME = "items"
    LOG_COLLECTION_NAME = "session_logs"
    COUNTER_COLLECTION_NAME = "log_counters"

    def __init__(self) -> None:
        from dotenv import dotenv_values

        try:
            config = dotenv_values(".env")
            self.URI = config["MONGODB_URI"]
        except Exception:
            ERROR_MESSAGE = "Failed to load MONGODB_URI from file `.env`. Make sure you have created the file and set the variable."
            raise ValueError(ERROR_MESSAGE)

        self.client = MongoClient(
            self.URI,
            server_api=ServerApi(version="1"),
        )
        self.db = self.client[self.DB_NAME]
        self.collection = self.db[self.ITEM_COLLECTION_NAME]
        self.log_collection = self.db[self.LOG_COLLECTION_NAME]
        self.counter_collection = self.db[self.COUNTER_COLLECTION_NAME]
        self.session_id = self.get_sessionid()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def close(self):
        """Close the connection."""
        self.client.close()

    def check_connection(self) -> bool:
        """Check if the connection is established."""

        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_sessionid(self) -> int:
        """Update the log counter, and return the current count."""

        self.counter_collection.update_one(
            {"_id": "logid"},
            {"$inc": {"seq": 1}},
        )

        counter = self.counter_collection.find_one({"_id": "logid"})
        if counter is None:
            raise ValueError("Counter is None, check the collection.")
        return counter["seq"]

    def log(self, info: SessionLogInfo | dict) -> SessionLog:
        """Create a log entry, and return the log id."""

        id = self.session_id
        content = SessionLog(
            id=id,
            time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            info=info,
        )
        self.log_collection.insert_one(content)
        return content

    def check_product(self, asin: str) -> bool:
        """Check if a product is in the database."""

        return self.collection.count_documents({"asin": asin}) > 0

    def find_product(self, asin: str) -> dict | None:
        """Find a product in the database."""

        return self.collection.find_one({"asin": asin})

    def update_product(self, product: SearchItem) -> bool:
        """Update a product in the database."""

        result = self.collection.update_one(
            {"asin": product["asin"]},
            {"$set": product},
            upsert=True,
        )

        return result.acknowledged

    def snapshot(self, download_path: str | None = None) -> list[dict]:
        """Download a snapshot of the collection and return the result."""

        cursor = self.collection.find({})
        if download_path is not None:
            with open(download_path, "w", encoding="utf-8") as f:
                f.write(json_util.dumps(list(cursor)))
            print(f"Snapshot is saved to {download_path}.")
        return list(cursor)


if __name__ == "__main__":
    uploader = DatabaseClient()
    uploader.client.admin.command("ping")
    print("Connection is established.")
