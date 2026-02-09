"""
Sentiment analysis service using Ollama local LLM.
Analyzes corporate text for trading sentiment with source-quality weighting.
"""
import json
import logging
import httpx
from ..config import settings
from ..models.sentiment import SentimentAnalysis

logger = logging.getLogger(__name__)

# Source type confidence multipliers
SOURCE_CONFIDENCE = {
    "earnings_call": 1.0,
    "press_release": 0.7,
    "news_article": 0.5,
}

SENTIMENT_PROMPT = """You are a financial analyst. Analyze the following corporate text for trading sentiment.

Source type: {source_type}
Ticker: {ticker}

Text:
{text}

Respond ONLY with valid JSON in this exact format (no other text):
{{
  "direction": "bullish" or "neutral" or "bearish",
  "score": <float from -1.0 (very bearish) to 1.0 (very bullish)>,
  "confidence": <float from 0.0 to 1.0 indicating how confident you are>,
  "reasoning": "<1-2 sentence explanation>"
}}

Rules:
- Do NOT quote specific financial numbers, percentages, or dollar amounts
- Base your assessment on tone, language, and strategic indicators
- Be conservative with extreme scores (only use >0.7 or <-0.7 for very clear signals)
"""


async def prewarm_model():
    """Pre-warm the Ollama model by sending a short prompt on startup."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            await client.post(
                f"{settings.ollama_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": "Hi", "stream": False},
            )
        logger.info(f"Ollama model {settings.ollama_model} pre-warmed")
    except Exception as e:
        logger.warning(f"Could not pre-warm Ollama model: {e}")


async def analyze_sentiment(
    text: str,
    source_type: str = "news_article",
    ticker: str = "",
) -> SentimentAnalysis:
    """
    Analyze corporate text for trading sentiment using Ollama.

    Args:
        text: Corporate text to analyze
        source_type: Type of source (earnings_call, press_release, news_article)
        ticker: Optional ticker for context

    Returns:
        SentimentAnalysis with direction, score, confidence, reasoning
    """
    prompt = SENTIMENT_PROMPT.format(
        source_type=source_type.replace("_", " "),
        ticker=ticker or "Unknown",
        text=text[:3000],  # Limit input to avoid context overflow
    )

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.ollama_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
            )
            resp.raise_for_status()
            result = resp.json()

        raw_response = result.get("response", "")
        parsed = _parse_llm_response(raw_response)

        # Apply source-quality confidence multiplier
        base_confidence = parsed.get("confidence", 0.5)
        multiplier = SOURCE_CONFIDENCE.get(source_type, 0.5)
        adjusted_confidence = min(base_confidence * multiplier, 1.0)

        return SentimentAnalysis(
            direction=parsed.get("direction", "neutral"),
            score=_clamp(parsed.get("score", 0.0), -1.0, 1.0),
            confidence=adjusted_confidence,
            reasoning=parsed.get("reasoning", "Unable to determine sentiment"),
            source_type=source_type,
        )

    except httpx.HTTPError as e:
        logger.error(f"Ollama request failed: {e}")
        return _fallback_sentiment(source_type)
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return _fallback_sentiment(source_type)


def _parse_llm_response(raw: str) -> dict:
    """Parse LLM JSON response with resilience to formatting issues."""
    raw = raw.strip()

    # Try direct JSON parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code block
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            cleaned = part.strip().removeprefix("json").strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    # Try finding JSON object in text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    logger.warning(f"Could not parse LLM response: {raw[:200]}")
    return {}


def _clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def _fallback_sentiment(source_type: str) -> SentimentAnalysis:
    """Return a neutral fallback when analysis fails."""
    return SentimentAnalysis(
        direction="neutral",
        score=0.0,
        confidence=0.1,
        reasoning="Analysis unavailable - Ollama service may be offline",
        source_type=source_type,
    )
