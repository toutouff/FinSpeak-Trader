from pydantic import BaseModel, Field
from datetime import datetime


class OHLCVData(BaseModel):
    """Single OHLCV data point."""

    date: datetime = Field(..., description="Date/time of the data point")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Trading volume")


class MarketDataResponse(BaseModel):
    """Market data response containing OHLCV data for a ticker."""

    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(..., description="Data timeframe (e.g., 'daily')")
    data_points: int = Field(..., description="Number of data points returned")
    data: list[OHLCVData] = Field(..., description="OHLCV data points")
