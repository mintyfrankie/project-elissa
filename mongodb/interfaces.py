"""
This module defines the data structures and classes used for interacting with a MongoDB database.

It includes the following classes and data structures:
- ItemMetadata: Represents the metadata of an item.
- ProductItem: Represents a product on Amazon.
- SessionLogInfo: Represents information about a session log.
- DatabaseCounter: Represents a database counter.
- SessionLog: Represents a session log.

"""

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


# ! Refactor this to be a dataclass / pydantic model
class SessionLogInfo(TypedDict):
    """A session log info."""

    action_type: str
    action_time: int
    update_count: int


# ! Refactor this to be a dataclass / pydantic model
class SessionLog(TypedDict):
    counter: int
    type: str
    time: datetime
    info: dict[str, str] | None


@dataclass
class DatabaseCounter:
    """
    Represents a database counter.

    Attributes:
        _id (str): The ID of the database counter.
        count (int): The count of the database counter.
    """

    _id: str = "log_counter"
    count: int = 0

    def get_id(self) -> dict[str, str]:
        """
        Get the ID of the database counter.

        Returns:
            dict[str, str]: The MongoDB query to get the ID of the database counter.
        """
        return {"_id": self._id}

    def increment_count(self) -> dict[str, dict[str, int]]:
        """
        Increment the count of the database counter.

        Returns:
            dict[str, dict[str, int]]: The MongoDB update query.
        """
        return {"$inc": {"count": 1}}
