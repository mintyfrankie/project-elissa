"""
Contain interfaces for data validation in the pipeline.
"""

from datetime import datetime
from typing import Literal, Optional

from matplotlib.image import thumbnail
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_serializer,
    field_validator,
)
from pydantic_core import Url

ScrapeStatus = Literal["SearchPage", "ProductPage", "ReviewPage"]


class ItemMetadata(BaseModel):
    """A metadata field of a document"""

    last_session_id: int
    last_session_time: datetime
    scrap_status: ScrapeStatus


class BaseItem(BaseModel):
    """A base item initialized by a SpiderWorker."""

    asin: str
    title: str | None
    thumbnail: HttpUrl | None
    metadata: Optional[ItemMetadata] = Field(None, serialization_alias="_metadata")

    @field_validator("asin")
    @classmethod
    def validate_asin(cls, v: str) -> str:
        """Validates the ASIN"""
        if not v.startswith("B0"):
            raise ValueError("ASIN must start with 'B0'")
        return v

    @field_serializer("thumbnail")
    def url2str(self, val) -> str:
        """Serialize the Url field to string"""
        if isinstance(val, Url):
            return str(val)
        return val


class ReviewItem(BaseModel):
    """A review on Amazon."""

    body: str | None
    rating: int | None
    title: str | None
    location: str | None
    date: str | None


class ProductItem(BaseModel):
    """A complete product document, extended by SpiderWorkers."""

    asin: Optional[str] = None  # Will be added later
    title: str | None
    thumbnail: HttpUrl | None
    price: float | None
    brand: str | None
    avg_rating: float | None
    num_reviews: int | None
    feature_bullets: list[str] | None
    unities: float | None
    review_url: HttpUrl | None
    category: str | None
    metadata: Optional[ItemMetadata] = Field(None, serialization_alias="_metadata")

    @field_serializer("review_url")
    @field_serializer("thumbnail")
    def url2str(self, val) -> str:
        """Serialize the Url field to string"""
        if isinstance(val, Url):
            return str(val)
        return val
