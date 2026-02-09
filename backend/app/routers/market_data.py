"""Market data API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from ..models.market import OHLCVData, MarketDataResponse
from ..services.influx_service import get_ohlcv

router = APIRouter(prefix="/api/market-data", tags=["Market Data"])


@router.get("/{ticker}", response_model=MarketDataResponse)
async def get_market_data(
    ticker: str,
    days: int = Query(default=180, ge=1, le=365, description="Days of history"),
):
    """Get cached OHLCV market data from InfluxDB."""
    ticker = ticker.upper()

    df = await get_ohlcv(ticker=ticker, days=days)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    data = [
        OHLCVData(
            date=row["date"],
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["volume"],
        )
        for _, row in df.iterrows()
    ]

    return MarketDataResponse(
        ticker=ticker,
        timeframe="daily",
        data_points=len(data),
        data=data,
    )
