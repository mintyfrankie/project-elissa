"""
Interfaces for data validation in the pipeline.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

SCRAP_STATUS = Literal["SearchPage", "ProductPage", "ReviewPage"]


class ItemMetadata(BaseModel):
    """Item metadata"""

    last_session_id: int
    last_session_time: datetime
    scrap_status: SCRAP_STATUS
