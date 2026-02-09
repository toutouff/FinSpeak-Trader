"""
RSI (Relative Strength Index) calculation.
Uses Wilder's smoothing method (exponential moving average).
"""
import numpy as np
import pandas as pd
from ...models.technical import RSIResult, TASignal


def calculate_rsi(
    df: pd.DataFrame,
    period: int = 14
) -> RSIResult:
    """
    Calculate RSI using Wilder's smoothing method.

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        period: RSI period (default 14)

    Returns:
        RSIResult with current RSI value and signal
    """
    if len(df) < period + 1:
        raise ValueError(f"Insufficient data for RSI calculation (need at least {period + 1} bars)")

    df = df.copy()

    # Calculate price changes
    df['change'] = df['close'].diff()

    # Separate gains and losses
    df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)
    df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)

    # Calculate first average (simple moving average for first period)
    first_avg_gain = df['gain'].iloc[1:period + 1].mean()
    first_avg_loss = df['loss'].iloc[1:period + 1].mean()

    # Wilder's smoothing (exponential moving average with alpha = 1/period)
    avg_gains = [first_avg_gain]
    avg_losses = [first_avg_loss]

    for i in range(period + 1, len(df)):
        avg_gain = (avg_gains[-1] * (period - 1) + df['gain'].iloc[i]) / period
        avg_loss = (avg_losses[-1] * (period - 1) + df['loss'].iloc[i]) / period
        avg_gains.append(avg_gain)
        avg_losses.append(avg_loss)

    # Calculate RS and RSI
    current_avg_gain = avg_gains[-1]
    current_avg_loss = avg_losses[-1]

    if current_avg_loss == 0:
        rsi = 100.0
    else:
        rs = current_avg_gain / current_avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

    # Generate signal
    signal = _generate_rsi_signal(rsi)

    return RSIResult(
        current_value=float(rsi),
        signal=signal
    )


def _generate_rsi_signal(rsi: float) -> TASignal:
    """
    Generate trading signal from RSI value.

    RSI > 70: Overbought (bearish)
    RSI < 30: Oversold (bullish)
    30 <= RSI <= 70: Neutral

    Confidence based on distance from 50 (midpoint).
    """
    if rsi > 70:
        direction = "bearish"
        # Confidence increases as RSI goes above 70
        # RSI 70 -> 0.5, RSI 100 -> 1.0
        confidence = 0.5 + (min(rsi - 70, 30) / 30) * 0.5
    elif rsi < 30:
        direction = "bullish"
        # Confidence increases as RSI goes below 30
        # RSI 30 -> 0.5, RSI 0 -> 1.0
        confidence = 0.5 + (min(30 - rsi, 30) / 30) * 0.5
    else:
        direction = "neutral"
        # Confidence inversely proportional to distance from extremes
        # RSI at 50 -> lowest confidence (0.1)
        # RSI near 30 or 70 -> higher confidence
        distance_from_50 = abs(rsi - 50)
        confidence = max(0.1, distance_from_50 / 50)

    confidence = max(0.0, min(1.0, confidence))

    return TASignal(
        direction=direction,
        confidence=confidence,
        details={
            "rsi": rsi,
            "overbought_threshold": 70,
            "oversold_threshold": 30
        }
    )
