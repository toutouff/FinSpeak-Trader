"""
MACD (Moving Average Convergence Divergence) calculation.
"""
import numpy as np
import pandas as pd
from ...models.technical import MACDResult, TASignal


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> MACDResult:
    """
    Calculate MACD indicator.

    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD, signal_period)
    Histogram = MACD Line - Signal Line

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)

    Returns:
        MACDResult with MACD line, signal line, histogram, and signal
    """
    min_length = slow_period + signal_period
    if len(df) < min_length:
        raise ValueError(f"Insufficient data for MACD calculation (need at least {min_length} bars)")

    df = df.copy()

    # Calculate EMAs
    ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()

    # MACD line
    macd_line = ema_fast - ema_slow

    # Signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Histogram
    histogram = macd_line - signal_line

    # Get current values
    current_macd = float(macd_line.iloc[-1])
    current_signal = float(signal_line.iloc[-1])
    current_histogram = float(histogram.iloc[-1])

    # Generate trading signal
    signal = _generate_macd_signal(
        macd_line.values,
        signal_line.values,
        current_macd,
        current_signal,
        current_histogram
    )

    return MACDResult(
        macd_line=current_macd,
        signal_line=current_signal,
        histogram=current_histogram,
        signal=signal
    )


def _generate_macd_signal(
    macd_series: np.ndarray,
    signal_series: np.ndarray,
    current_macd: float,
    current_signal: float,
    current_histogram: float
) -> TASignal:
    """
    Generate trading signal from MACD.

    MACD above Signal: Bullish
    MACD below Signal: Bearish
    Recent crossover: Higher confidence
    """
    # Determine direction
    if current_macd > current_signal:
        direction = "bullish"
    elif current_macd < current_signal:
        direction = "bearish"
    else:
        direction = "neutral"

    # Check for recent crossover (last 3 bars)
    crossover_detected = False
    lookback = min(3, len(macd_series) - 1)

    for i in range(1, lookback + 1):
        prev_macd = macd_series[-i - 1]
        prev_signal = signal_series[-i - 1]

        # Bullish crossover: MACD crossed above signal
        if direction == "bullish" and prev_macd <= prev_signal and current_macd > current_signal:
            crossover_detected = True
            break

        # Bearish crossover: MACD crossed below signal
        if direction == "bearish" and prev_macd >= prev_signal and current_macd < current_signal:
            crossover_detected = True
            break

    # Calculate confidence
    if direction == "neutral":
        confidence = 0.1
    else:
        # Base confidence on histogram magnitude (distance between MACD and signal)
        # Normalize by MACD value to make it relative
        if abs(current_macd) > 0.01:
            histogram_ratio = abs(current_histogram) / abs(current_macd)
            base_confidence = min(histogram_ratio * 2, 0.7)  # Cap at 0.7
        else:
            base_confidence = 0.3

        # Boost confidence if crossover detected
        if crossover_detected:
            confidence = min(base_confidence * 1.4, 1.0)
        else:
            confidence = base_confidence

    confidence = max(0.0, min(1.0, confidence))

    return TASignal(
        direction=direction,
        confidence=confidence,
        details={
            "macd": current_macd,
            "signal": current_signal,
            "histogram": current_histogram,
            "crossover_detected": crossover_detected
        }
    )
