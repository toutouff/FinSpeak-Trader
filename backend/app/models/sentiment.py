from pydantic import BaseModel, Field
from typing import Literal


class SentimentRequest(BaseModel):
    """Request body for sentiment analysis."""

    text: str = Field(..., description="Corporate text to analyze")
    source_type: Literal["earnings_call", "press_release", "news_article"] = Field(
        "news_article", description="Source type affects confidence weighting"
    )
    ticker: str = Field("", description="Optional ticker for context")


class SentimentAnalysis(BaseModel):
    """Result of sentiment analysis on corporate text."""

    direction: Literal["bullish", "neutral", "bearish"] = Field(
        ..., description="Overall sentiment direction"
    )
    score: float = Field(
        ..., ge=-1.0, le=1.0, description="Sentiment score (-1 bearish to +1 bullish)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the analysis"
    )
    reasoning: str = Field(..., description="Brief explanation of sentiment assessment")
    source_type: str = Field(..., description="Source type used for analysis")
