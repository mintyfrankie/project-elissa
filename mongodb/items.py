from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


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


class SessionLog(TypedDict):
    counter: int
    type: str
    time: datetime
    info: dict[str, str] | None
