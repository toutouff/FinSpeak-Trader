"""Tests for Phase 1 - Service logic (sentiment parsing, corporate caching)."""
import pytest
from app.services.sentiment_service import _parse_llm_response, _clamp, _fallback_sentiment


# ============================================================
# LLM Response Parsing
# ============================================================

class TestLLMResponseParsing:
    def test_parse_clean_json(self):
        raw = '{"direction": "bullish", "score": 0.6, "confidence": 0.8, "reasoning": "Strong growth"}'
        result = _parse_llm_response(raw)
        assert result["direction"] == "bullish"
        assert result["score"] == 0.6

    def test_parse_json_with_markdown_block(self):
        raw = '```json\n{"direction": "bearish", "score": -0.3, "confidence": 0.5, "reasoning": "Weak"}\n```'
        result = _parse_llm_response(raw)
        assert result["direction"] == "bearish"

    def test_parse_json_with_surrounding_text(self):
        raw = 'Here is my analysis:\n{"direction": "neutral", "score": 0.0, "confidence": 0.4, "reasoning": "Mixed signals"}\nEnd.'
        result = _parse_llm_response(raw)
        assert result["direction"] == "neutral"

    def test_parse_empty_string_returns_empty(self):
        result = _parse_llm_response("")
        assert result == {}

    def test_parse_invalid_json_returns_empty(self):
        result = _parse_llm_response("This is not JSON at all")
        assert result == {}

    def test_parse_json_with_extra_whitespace(self):
        raw = '  \n  {"direction": "bullish", "score": 0.5, "confidence": 0.7, "reasoning": "ok"}  \n  '
        result = _parse_llm_response(raw)
        assert result["direction"] == "bullish"


# ============================================================
# Utility Functions
# ============================================================

class TestClamp:
    def test_clamp_within_range(self):
        assert _clamp(0.5, 0.0, 1.0) == 0.5

    def test_clamp_below_min(self):
        assert _clamp(-0.5, 0.0, 1.0) == 0.0

    def test_clamp_above_max(self):
        assert _clamp(1.5, 0.0, 1.0) == 1.0

    def test_clamp_at_boundaries(self):
        assert _clamp(0.0, 0.0, 1.0) == 0.0
        assert _clamp(1.0, 0.0, 1.0) == 1.0


# ============================================================
# Fallback Sentiment
# ============================================================

class TestFallbackSentiment:
    def test_fallback_is_neutral(self):
        result = _fallback_sentiment("earnings_call")
        assert result.direction == "neutral"
        assert result.score == 0.0
        assert result.confidence == 0.1

    def test_fallback_preserves_source_type(self):
        result = _fallback_sentiment("press_release")
        assert result.source_type == "press_release"


# ============================================================
# Confidence Multipliers
# ============================================================

class TestConfidenceWeighting:
    def test_earnings_call_highest_weight(self):
        from app.services.sentiment_service import SOURCE_CONFIDENCE
        assert SOURCE_CONFIDENCE["earnings_call"] > SOURCE_CONFIDENCE["press_release"]
        assert SOURCE_CONFIDENCE["press_release"] > SOURCE_CONFIDENCE["news_article"]

    def test_earnings_call_is_1_0(self):
        from app.services.sentiment_service import SOURCE_CONFIDENCE
        assert SOURCE_CONFIDENCE["earnings_call"] == 1.0

    def test_news_article_is_lowest(self):
        from app.services.sentiment_service import SOURCE_CONFIDENCE
        assert SOURCE_CONFIDENCE["news_article"] == 0.5
