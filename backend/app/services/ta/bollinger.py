"""
Bollinger Bands calculation.
"""
import numpy as np
import pandas as pd
from ...models.technical import BollingerResult, TASignal


def calculate_bollinger(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> BollingerResult:
    """
    Calculate Bollinger Bands.

    Middle Band = SMA(period)
    Upper Band = Middle + (std_dev * standard deviation)
    Lower Band = Middle - (std_dev * standard deviation)

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        period: SMA period (default 20)
        std_dev: Number of standard deviations (default 2.0)

    Returns:
        BollingerResult with bands, bandwidth, squeeze detection, and signal
    """
    if len(df) < period * 2:
        raise ValueError(f"Insufficient data for Bollinger calculation (need at least {period * 2} bars)")

    df = df.copy()

    # Calculate middle band (SMA)
    middle = df['close'].rolling(window=period).mean()

    # Calculate standard deviation
    std = df['close'].rolling(window=period).std()

    # Calculate upper and lower bands
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)

    # Calculate bandwidth
    bandwidth = (upper - lower) / middle

    # Current values
    current_upper = float(upper.iloc[-1])
    current_middle = float(middle.iloc[-1])
    current_lower = float(lower.iloc[-1])
    current_bandwidth = float(bandwidth.iloc[-1])
    current_price = float(df['close'].iloc[-1])

    # Detect squeeze (bandwidth < its SMA * 0.75)
    bandwidth_sma = bandwidth.rolling(window=period).mean()
    current_bandwidth_sma = float(bandwidth_sma.iloc[-1])
    squeeze = current_bandwidth < (current_bandwidth_sma * 0.75)

    # Generate signal
    signal = _generate_bollinger_signal(
        current_price,
        current_upper,
        current_middle,
        current_lower,
        current_bandwidth,
        squeeze
    )

    return BollingerResult(
        upper=current_upper,
        middle=current_middle,
        lower=current_lower,
        bandwidth=current_bandwidth,
        squeeze=squeeze,
        signal=signal
    )


def _generate_bollinger_signal(
    price: float,
    upper: float,
    middle: float,
    lower: float,
    bandwidth: float,
    squeeze: bool
) -> TASignal:
    """
    Generate trading signal from Bollinger Bands.

    Price near lower band: Bullish (oversold)
    Price near upper band: Bearish (overbought)
    Squeeze: Neutral (pending breakout)
    """
    # Calculate band width
    band_range = upper - lower
    if band_range == 0:
        return TASignal(direction="neutral", confidence=0.1, details={})

    # Calculate price position within bands (0 = lower, 1 = upper)
    price_position = (price - lower) / band_range

    # Determine direction and confidence
    if squeeze:
        # Squeeze detected - pending breakout, neutral
        direction = "neutral"
        confidence = 0.6  # Moderate confidence that a breakout is pending
        details = {
            "squeeze": True,
            "price_position": price_position,
            "reason": "Bollinger squeeze detected - pending breakout"
        }
    elif price_position < 0.2:
        # Near lower band - bullish
        direction = "bullish"
        # Closer to lower band = higher confidence
        confidence = max(0.5, 1.0 - price_position * 2.5)
        details = {
            "squeeze": False,
            "price_position": price_position,
            "reason": "Price near lower Bollinger Band"
        }
    elif price_position > 0.8:
        # Near upper band - bearish
        direction = "bearish"
        # Closer to upper band = higher confidence
        confidence = max(0.5, (price_position - 0.6) * 2.5)
        details = {
            "squeeze": False,
            "price_position": price_position,
            "reason": "Price near upper Bollinger Band"
        }
    else:
        # Middle of bands - neutral
        direction = "neutral"
        # Confidence based on distance from middle (50%)
        distance_from_middle = abs(price_position - 0.5)
        confidence = max(0.2, distance_from_middle * 2)
        details = {
            "squeeze": False,
            "price_position": price_position,
            "reason": "Price in middle of Bollinger Bands"
        }

    confidence = max(0.0, min(1.0, confidence))

    return TASignal(
        direction=direction,
        confidence=confidence,
        details=details
    )
