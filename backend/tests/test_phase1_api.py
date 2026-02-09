"""Tests for Phase 1 - API endpoint integration (using FastAPI TestClient)."""
import pytest
from unittest.mock import patch, AsyncMock
import pandas as pd
from datetime import datetime
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked settings."""
    # Patch settings before importing app to avoid .env requirement
    with patch("app.config.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.influxdb_url = "http://localhost:8086"
        mock_settings.influxdb_token = "test-token"
        mock_settings.influxdb_org = "finspeak"
        mock_settings.influxdb_bucket = "market_data"
        mock_settings.fmp_api_key = "test-key"
        mock_settings.ollama_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama3.1:8b"
        mock_settings.cors_origins = ["http://localhost:3000"]
        mock_settings.alpha_api_key = ""

        # Patch prewarm and health check to avoid real connections
        with patch("app.services.sentiment_service.prewarm_model", new_callable=AsyncMock):
            with patch("app.services.influx_service.check_health", new_callable=AsyncMock, return_value=True):
                from app.main import app
                yield TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        with patch("app.services.influx_service.check_health", new_callable=AsyncMock, return_value=True):
            resp = client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"


class TestMarketDataEndpoint:
    def test_get_market_data_success(self, client):
        mock_df = pd.DataFrame({
            "date": [datetime(2026, 2, 7)],
            "open": [180.0],
            "high": [185.0],
            "low": [179.0],
            "close": [183.5],
            "volume": [55e6],
        })
        with patch("app.routers.market_data.get_ohlcv", new_callable=AsyncMock, return_value=mock_df):
            resp = client.get("/api/market-data/AAPL")
            assert resp.status_code == 200
            data = resp.json()
            assert data["ticker"] == "AAPL"
            assert data["data_points"] == 1
            assert len(data["data"]) == 1
            assert data["data"][0]["close"] == 183.5

    def test_get_market_data_not_found(self, client):
        with patch("app.routers.market_data.get_ohlcv", new_callable=AsyncMock, return_value=pd.DataFrame()):
            resp = client.get("/api/market-data/INVALID")
            assert resp.status_code == 404


class TestSentimentEndpoint:
    def test_sentiment_analyze(self, client):
        mock_result = {
            "direction": "bullish",
            "score": 0.6,
            "confidence": 0.8,
            "reasoning": "Strong growth indicators",
            "source_type": "earnings_call",
        }
        with patch("app.routers.sentiment.analyze_sentiment", new_callable=AsyncMock, return_value=mock_result):
            resp = client.post("/api/sentiment/analyze", json={
                "text": "Revenue exceeded expectations significantly",
                "source_type": "earnings_call",
                "ticker": "AAPL",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["direction"] == "bullish"

    def test_sentiment_requires_text(self, client):
        resp = client.post("/api/sentiment/analyze", json={})
        assert resp.status_code == 422  # validation error


class TestCorporateDataEndpoint:
    def test_get_corporate_data_success(self, client):
        mock_docs = [
            {
                "title": "AAPL Q4 Earnings",
                "content": "Revenue grew...",
                "source_type": "earnings_call",
                "date": None,
                "ticker": "AAPL",
            }
        ]
        with patch("app.routers.corporate_data.fetch_all_corporate_data", new_callable=AsyncMock, return_value=mock_docs):
            resp = client.get("/api/corporate-data/AAPL")
            assert resp.status_code == 200
            data = resp.json()
            assert data["ticker"] == "AAPL"
            assert data["total"] == 1

    def test_get_corporate_data_empty(self, client):
        with patch("app.routers.corporate_data.fetch_all_corporate_data", new_callable=AsyncMock, return_value=[]):
            resp = client.get("/api/corporate-data/AAPL")
            assert resp.status_code == 404
