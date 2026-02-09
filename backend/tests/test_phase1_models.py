"""Tests for Phase 1 - Pydantic models and service logic."""
import pytest
from datetime import datetime
from app.models.market import OHLCVData, MarketDataResponse
from app.models.corporate import CorporateDocument, CorporateDataResponse
from app.models.sentiment import SentimentRequest, SentimentAnalysis


# ============================================================
# Market Data Models
# ============================================================

class TestMarketModels:
    def test_ohlcv_data_creation(self):
        data = OHLCVData(
            date=datetime(2026, 2, 7),
            open=180.0,
            high=185.0,
            low=179.0,
            close=183.5,
            volume=55_000_000.0,
        )
        assert data.close == 183.5
        assert data.volume == 55_000_000.0

    def test_market_data_response(self):
        item = OHLCVData(
            date=datetime(2026, 2, 7),
            open=180.0, high=185.0, low=179.0, close=183.5, volume=55e6,
        )
        resp = MarketDataResponse(
            ticker="AAPL",
            timeframe="daily",
            data_points=1,
            data=[item],
        )
        assert resp.ticker == "AAPL"
        assert resp.data_points == 1
        assert len(resp.data) == 1


# ============================================================
# Corporate Data Models
# ============================================================

class TestCorporateModels:
    def test_earnings_call_document(self):
        doc = CorporateDocument(
            title="AAPL Q4 2024 Earnings Call",
            content="Revenue exceeded expectations...",
            source_type="earnings_call",
            ticker="AAPL",
        )
        assert doc.source_type == "earnings_call"
        assert doc.ticker == "AAPL"

    def test_news_article_document(self):
        doc = CorporateDocument(
            title="Apple announces new product",
            content="Apple Inc. today announced...",
            source_type="news_article",
            ticker="AAPL",
            date=datetime(2026, 1, 15),
        )
        assert doc.source_type == "news_article"

    def test_press_release_document(self):
        doc = CorporateDocument(
            title="Apple Reports Q4 Results",
            content="CUPERTINO — Apple today announced...",
            source_type="press_release",
            ticker="AAPL",
        )
        assert doc.source_type == "press_release"

    def test_invalid_source_type_rejected(self):
        with pytest.raises(Exception):
            CorporateDocument(
                title="Test",
                content="Test content",
                source_type="blog_post",  # invalid
                ticker="AAPL",
            )

    def test_corporate_response(self):
        doc = CorporateDocument(
            title="Test", content="Content",
            source_type="earnings_call", ticker="AAPL",
        )
        resp = CorporateDataResponse(ticker="AAPL", documents=[doc], total=1)
        assert resp.total == 1


# ============================================================
# Sentiment Models
# ============================================================

class TestSentimentModels:
    def test_sentiment_request(self):
        req = SentimentRequest(
            text="Revenue grew significantly this quarter",
            source_type="earnings_call",
            ticker="AAPL",
        )
        assert req.source_type == "earnings_call"

    def test_sentiment_request_defaults(self):
        req = SentimentRequest(text="Some text")
        assert req.source_type == "news_article"
        assert req.ticker == ""

    def test_sentiment_analysis_bullish(self):
        result = SentimentAnalysis(
            direction="bullish",
            score=0.7,
            confidence=0.85,
            reasoning="Strong revenue growth signals positive outlook",
            source_type="earnings_call",
        )
        assert result.direction == "bullish"
        assert result.score == 0.7
        assert result.confidence == 0.85

    def test_sentiment_analysis_bearish(self):
        result = SentimentAnalysis(
            direction="bearish",
            score=-0.5,
            confidence=0.6,
            reasoning="Declining margins suggest challenges ahead",
            source_type="press_release",
        )
        assert result.direction == "bearish"
        assert -1.0 <= result.score <= 1.0

    def test_score_bounds_enforced(self):
        with pytest.raises(Exception):
            SentimentAnalysis(
                direction="neutral", score=1.5,  # out of bounds
                confidence=0.5, reasoning="test", source_type="news_article",
            )

    def test_confidence_bounds_enforced(self):
        with pytest.raises(Exception):
            SentimentAnalysis(
                direction="neutral", score=0.0,
                confidence=1.5,  # out of bounds
                reasoning="test", source_type="news_article",
            )
