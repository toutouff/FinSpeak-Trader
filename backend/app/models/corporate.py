from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class CorporateDocument(BaseModel):
    """A single corporate communication document."""

    title: str = Field(..., description="Document title or headline")
    content: str = Field(..., description="Full text content")
    source_type: Literal["earnings_call", "press_release", "news_article"] = Field(
        ..., description="Type of corporate communication"
    )
    date: datetime | None = Field(None, description="Publication date")
    ticker: str = Field(..., description="Associated ticker symbol")


class CorporateDataResponse(BaseModel):
    """Response containing corporate communications for a ticker."""

    ticker: str
    documents: list[CorporateDocument]
    total: int = Field(..., description="Number of documents returned")
