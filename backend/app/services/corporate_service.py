"""
Corporate data service using Financial Modeling Prep API.
Fetches earnings transcripts, press releases, and news articles.
"""
import logging
import time
from datetime import datetime
import httpx
from ..config import settings
from ..models.corporate import CorporateDocument

logger = logging.getLogger(__name__)

# Simple in-memory cache: key -> (data, timestamp)
_cache: dict[str, tuple[list[CorporateDocument], float]] = {}
CACHE_TTL = 3600  # 1 hour

FMP_BASE = "https://financialmodelingprep.com/api/v3"


def _get_cached(key: str) -> list[CorporateDocument] | None:
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cache(key: str, data: list[CorporateDocument]):
    _cache[key] = (data, time.time())


async def fetch_earnings_transcripts(ticker: str, year: int = 2024, quarter: int = 4) -> list[CorporateDocument]:
    """Fetch earnings call transcripts from FMP."""
    cache_key = f"earnings:{ticker}:{year}:{quarter}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    if not settings.fmp_api_key:
        logger.warning("FMP_API_KEY not set, returning empty earnings data")
        return []

    url = f"{FMP_BASE}/earning_call_transcript/{ticker}"
    params = {"year": year, "quarter": quarter, "apikey": settings.fmp_api_key}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if not isinstance(data, list):
            data = [data] if data else []

        docs = []
        for item in data:
            content = item.get("content", "")
            if not content:
                continue
            docs.append(CorporateDocument(
                title=f"{ticker} Earnings Call Q{quarter} {year}",
                content=content[:5000],  # Limit content size for LLM
                source_type="earnings_call",
                date=datetime.fromisoformat(item["date"]) if item.get("date") else None,
                ticker=ticker,
            ))

        _set_cache(cache_key, docs)
        logger.info(f"Fetched {len(docs)} earnings transcripts for {ticker}")
        return docs

    except httpx.HTTPError as e:
        logger.error(f"FMP earnings API error for {ticker}: {e}")
        return []


async def fetch_news(ticker: str, limit: int = 5) -> list[CorporateDocument]:
    """Fetch stock news from FMP."""
    cache_key = f"news:{ticker}:{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    if not settings.fmp_api_key:
        logger.warning("FMP_API_KEY not set, returning empty news data")
        return []

    url = f"{FMP_BASE}/stock_news"
    params = {"tickers": ticker, "limit": limit, "apikey": settings.fmp_api_key}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        docs = []
        for item in data:
            text = item.get("text", "")
            title = item.get("title", "")
            if not text and not title:
                continue
            docs.append(CorporateDocument(
                title=title or f"{ticker} News",
                content=text[:3000] if text else title,
                source_type="news_article",
                date=datetime.fromisoformat(item["publishedDate"]) if item.get("publishedDate") else None,
                ticker=ticker,
            ))

        _set_cache(cache_key, docs)
        logger.info(f"Fetched {len(docs)} news articles for {ticker}")
        return docs

    except httpx.HTTPError as e:
        logger.error(f"FMP news API error for {ticker}: {e}")
        return []


async def fetch_press_releases(ticker: str, limit: int = 5) -> list[CorporateDocument]:
    """Fetch press releases from FMP."""
    cache_key = f"press:{ticker}:{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    if not settings.fmp_api_key:
        logger.warning("FMP_API_KEY not set, returning empty press release data")
        return []

    url = f"{FMP_BASE}/press-releases/{ticker}"
    params = {"limit": limit, "apikey": settings.fmp_api_key}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        docs = []
        for item in data:
            text = item.get("text", "")
            title = item.get("title", "")
            if not text and not title:
                continue
            docs.append(CorporateDocument(
                title=title or f"{ticker} Press Release",
                content=text[:3000] if text else title,
                source_type="press_release",
                date=datetime.fromisoformat(item["date"]) if item.get("date") else None,
                ticker=ticker,
            ))

        _set_cache(cache_key, docs)
        logger.info(f"Fetched {len(docs)} press releases for {ticker}")
        return docs

    except httpx.HTTPError as e:
        logger.error(f"FMP press releases API error for {ticker}: {e}")
        return []


async def fetch_all_corporate_data(ticker: str) -> list[CorporateDocument]:
    """Fetch all types of corporate data for a ticker."""
    import asyncio
    earnings, news, press = await asyncio.gather(
        fetch_earnings_transcripts(ticker),
        fetch_news(ticker),
        fetch_press_releases(ticker),
    )
    return earnings + press + news
