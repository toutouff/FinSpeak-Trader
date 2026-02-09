"""
Technical Analysis API endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from ..models.technical import TechnicalAnalysisBundle
from ..services.ta import (
    calculate_volume_profile,
    calculate_support_resistance,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger,
    calculate_ichimoku,
    calculate_convergence,
)

# Import will be available once Phase 1 completes
try:
    from ..services.influx_service import get_ohlcv
except ImportError:
    # Phase 1 not complete yet - create placeholder
    async def get_ohlcv(ticker: str, days: int = 180):
        """Placeholder for influx_service - will be implemented in Phase 1."""
        raise HTTPException(
            status_code=503,
            detail="Data service not yet available - Phase 1 in progress"
        )


router = APIRouter(prefix="/api/technical", tags=["Technical Analysis"])


@router.get("/{ticker}", response_model=TechnicalAnalysisBundle)
async def get_technical_analysis(
    ticker: str,
    days: int = Query(default=180, ge=60, le=365, description="Number of days of historical data")
) -> TechnicalAnalysisBundle:
    """
    Get comprehensive technical analysis for a ticker.

    Calculates:
    - Volume Profile (VPOC, VAH, VAL)
    - Support & Resistance levels
    - RSI
    - MACD
    - Bollinger Bands
    - Ichimoku Cloud
    - Convergence score across all methods

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of days of historical data (60-365, default 180)

    Returns:
        TechnicalAnalysisBundle with all TA results
    """
    ticker = ticker.upper()

    try:
        # Get OHLCV data from InfluxDB
        df = await get_ohlcv(ticker=ticker, days=days)

        if df is None or len(df) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}"
            )

        # Calculate all technical indicators
        volume_profile = calculate_volume_profile(df)
        support_resistance = calculate_support_resistance(df)
        rsi = calculate_rsi(df)
        macd = calculate_macd(df)
        bollinger = calculate_bollinger(df)
        ichimoku = calculate_ichimoku(df)

        # Calculate convergence
        convergence = calculate_convergence(
            rsi_signal=rsi.signal,
            macd_signal=macd.signal,
            bollinger_signal=bollinger.signal,
            ichimoku_signal=ichimoku.signal
        )

        # Build response bundle
        return TechnicalAnalysisBundle(
            ticker=ticker,
            timestamp=datetime.now(),
            volume_profile=volume_profile,
            support_resistance=support_resistance,
            rsi=rsi,
            macd=macd,
            bollinger=bollinger,
            ichimoku=ichimoku,
            convergence=convergence
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating technical analysis: {str(e)}"
        )
