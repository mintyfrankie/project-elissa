"""
Interfaces for data validation in the pipeline.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_serializer,
    field_validator,
)
from pydantic_core import Url

SCRAP_STATUS = Literal["SearchPage", "ProductPage", "ReviewPage"]


class ItemMetadata(BaseModel):
    """Item metadata"""

    last_session_id: int
    last_session_time: datetime
    scrap_status: SCRAP_STATUS
    SearchItemScraper_version: Optional[int] = None
    ProductItemScraper_version: Optional[int] = None
    ReviewItemScraper_version: Optional[int] = None


class BaseItem(BaseModel):
    """A base item added by SearchPageSpiderWorker"""

    asin: str
    title: str | None
    thumbnail: HttpUrl | None
    metadata: Optional[ItemMetadata] = Field(..., serialization_alias="_metadata")

    @field_validator("asin")
    @classmethod
    def validate_asin(cls, v: str) -> str:
        """Validates the ASIN"""
        if not v.startswith("B0"):
            raise ValueError("ASIN must start with 'B0'")
        return v

    @field_serializer("thumbnail")
    def url2str(self, val) -> str:
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


class ProductItem(BaseItem):
    """A complete product document, extended by ProductPageSpiderWorker and ReviewPageSpiderWorker."""

    brand: str
    price: float | None
    unities: float | None
    avg_rating: float | None
    num_reviews: int | None
    features_bullets: list[str] | None
    review_url: HttpUrl | None
    reviews: Optional[list[ReviewItem]] = None

    @field_serializer("review_url")
    def url2str(self, val) -> str:
        if isinstance(val, Url):
            return str(val)
        return val
