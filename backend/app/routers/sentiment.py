"""Sentiment analysis API endpoints."""
from fastapi import APIRouter
from ..models.sentiment import SentimentRequest, SentimentAnalysis
from ..services.sentiment_service import analyze_sentiment

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])


@router.post("/analyze", response_model=SentimentAnalysis)
async def analyze(request: SentimentRequest) -> SentimentAnalysis:
    """
    Analyze corporate text for trading sentiment using Ollama LLM.

    Returns direction (bullish/neutral/bearish), score, confidence, and reasoning.
    Confidence is weighted by source type: earnings_call > press_release > news_article.
    """
    return await analyze_sentiment(
        text=request.text,
        source_type=request.source_type,
        ticker=request.ticker,
    )
