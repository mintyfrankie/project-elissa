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

from pydantic import BaseModel, ConfigDict


class SessionLogInfo(BaseModel):
    """A session log info that scarping workers pass to log their actions."""

    model_config = ConfigDict(extra="allow")

    update_count: int


class SessionLog(BaseModel):
    """A session log."""

    id: int
    time: datetime
    action_type: str
    info: SessionLogInfo | None


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
