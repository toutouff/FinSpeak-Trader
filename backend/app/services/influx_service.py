"""
InfluxDB service for querying cached OHLCV market data.
Reuses patterns from influx-populate-script.py.
"""
import logging
import pandas as pd
from influxdb_client import InfluxDBClient
from ..config import settings

logger = logging.getLogger(__name__)

# Module-level client (reused across requests)
_client: InfluxDBClient | None = None


def _get_client() -> InfluxDBClient:
    global _client
    if _client is None:
        _client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
            timeout=30_000,
        )
    return _client


async def get_ohlcv(ticker: str, days: int = 180) -> pd.DataFrame:
    """
    Query InfluxDB for cached OHLCV data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
        days: Number of days of historical data

    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    client = _get_client()
    query_api = client.query_api()

    query = f'''
    from(bucket: "{settings.influxdb_bucket}")
        |> range(start: -{days}d)
        |> filter(fn: (r) => r._measurement == "stock_price")
        |> filter(fn: (r) => r.symbol == "{ticker}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"])
    '''

    try:
        result = query_api.query_data_frame(query)
    except Exception as e:
        logger.error(f"InfluxDB query failed for {ticker}: {e}")
        return pd.DataFrame()

    if isinstance(result, list):
        if not result:
            return pd.DataFrame()
        result = pd.concat(result, ignore_index=True)

    if result.empty:
        return pd.DataFrame()

    # Clean up columns to match expected format
    drop_cols = [c for c in ["result", "table", "_measurement", "_start", "_stop", "symbol", "timeframe"] if c in result.columns]
    result = result.drop(columns=drop_cols, errors="ignore")

    if "_time" in result.columns:
        result = result.rename(columns={"_time": "date"})

    # Ensure required columns exist
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in result.columns:
            logger.warning(f"Missing column {col} in InfluxDB result for {ticker}")
            return pd.DataFrame()

    result = result.sort_values("date").reset_index(drop=True)
    logger.info(f"Retrieved {len(result)} data points for {ticker}")
    return result


async def check_health() -> bool:
    """Check InfluxDB connectivity."""
    try:
        client = _get_client()
        health = client.health()
        return health.status == "pass"
    except Exception:
        return False
