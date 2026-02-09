"""
Ichimoku Cloud calculation.
"""
import numpy as np
import pandas as pd
from ...models.technical import IchimokuResult, TASignal


def calculate_ichimoku(
    df: pd.DataFrame,
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_b_period: int = 52
) -> IchimokuResult:
    """
    Calculate Ichimoku Cloud indicator.

    Tenkan-sen (Conversion Line) = (9-period high + 9-period low) / 2
    Kijun-sen (Base Line) = (26-period high + 26-period low) / 2
    Senkou Span A = (Tenkan + Kijun) / 2, plotted 26 periods ahead
    Senkou Span B = (52-period high + 52-period low) / 2, plotted 26 periods ahead
    Chikou Span = Current close, plotted 26 periods back

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        tenkan_period: Conversion line period (default 9)
        kijun_period: Base line period (default 26)
        senkou_b_period: Leading Span B period (default 52)

    Returns:
        IchimokuResult with all Ichimoku components and signal
    """
    min_length = senkou_b_period + kijun_period
    if len(df) < min_length:
        raise ValueError(f"Insufficient data for Ichimoku calculation (need at least {min_length} bars)")

    df = df.copy()

    # Calculate Tenkan-sen (Conversion Line)
    tenkan_high = df['high'].rolling(window=tenkan_period).max()
    tenkan_low = df['low'].rolling(window=tenkan_period).min()
    tenkan_sen = (tenkan_high + tenkan_low) / 2

    # Calculate Kijun-sen (Base Line)
    kijun_high = df['high'].rolling(window=kijun_period).max()
    kijun_low = df['low'].rolling(window=kijun_period).min()
    kijun_sen = (kijun_high + kijun_low) / 2

    # Calculate Senkou Span A (Leading Span A)
    senkou_span_a = (tenkan_sen + kijun_sen) / 2

    # Calculate Senkou Span B (Leading Span B)
    senkou_b_high = df['high'].rolling(window=senkou_b_period).max()
    senkou_b_low = df['low'].rolling(window=senkou_b_period).min()
    senkou_span_b = (senkou_b_high + senkou_b_low) / 2

    # Chikou Span (Lagging Span) = current close
    chikou_span = df['close']

    # Get current values
    # For Senkou Spans, we use values from 26 periods ago (since they're plotted ahead)
    # This gives us the "current" cloud position
    current_tenkan = float(tenkan_sen.iloc[-1])
    current_kijun = float(kijun_sen.iloc[-1])
    current_price = float(df['close'].iloc[-1])

    # Current cloud: Senkou values from 26 periods ago
    if len(df) >= kijun_period * 2:
        current_senkou_a = float(senkou_span_a.iloc[-kijun_period])
        current_senkou_b = float(senkou_span_b.iloc[-kijun_period])
    else:
        # Not enough data for proper cloud positioning
        current_senkou_a = float(senkou_span_a.iloc[-1])
        current_senkou_b = float(senkou_span_b.iloc[-1])

    current_chikou = float(chikou_span.iloc[-1])

    # Generate signal
    signal = _generate_ichimoku_signal(
        current_price,
        current_tenkan,
        current_kijun,
        current_senkou_a,
        current_senkou_b
    )

    return IchimokuResult(
        tenkan_sen=current_tenkan,
        kijun_sen=current_kijun,
        senkou_span_a=current_senkou_a,
        senkou_span_b=current_senkou_b,
        chikou_span=current_chikou,
        signal=signal
    )


def _generate_ichimoku_signal(
    price: float,
    tenkan: float,
    kijun: float,
    senkou_a: float,
    senkou_b: float
) -> TASignal:
    """
    Generate trading signal from Ichimoku Cloud.

    Price above cloud: Bullish
    Price below cloud: Bearish
    Price inside cloud: Neutral
    Cloud color (Senkou A > Senkou B): Bullish cloud
    """
    # Determine cloud boundaries
    cloud_top = max(senkou_a, senkou_b)
    cloud_bottom = min(senkou_a, senkou_b)

    # Determine price position relative to cloud
    if price > cloud_top:
        direction = "bullish"
        # Distance above cloud increases confidence
        cloud_height = cloud_top - cloud_bottom if cloud_top != cloud_bottom else price * 0.01
        distance_above = (price - cloud_top) / cloud_height
        base_confidence = min(0.5 + distance_above * 0.3, 0.9)
    elif price < cloud_bottom:
        direction = "bearish"
        # Distance below cloud increases confidence
        cloud_height = cloud_top - cloud_bottom if cloud_top != cloud_bottom else price * 0.01
        distance_below = (cloud_bottom - price) / cloud_height
        base_confidence = min(0.5 + distance_below * 0.3, 0.9)
    else:
        # Inside cloud
        direction = "neutral"
        base_confidence = 0.3

    # Cloud color analysis (additional confirmation)
    cloud_bullish = senkou_a > senkou_b

    # TK Cross analysis (Tenkan vs Kijun)
    tk_bullish = tenkan > kijun

    # Adjust confidence based on confirmations
    confirmations = 0
    if direction == "bullish":
        if cloud_bullish:
            confirmations += 1
        if tk_bullish:
            confirmations += 1
    elif direction == "bearish":
        if not cloud_bullish:
            confirmations += 1
        if not tk_bullish:
            confirmations += 1

    # Boost confidence with confirmations
    confidence = base_confidence
    if confirmations > 0:
        confidence = min(confidence * (1 + confirmations * 0.15), 1.0)

    confidence = max(0.0, min(1.0, confidence))

    return TASignal(
        direction=direction,
        confidence=confidence,
        details={
            "price_vs_cloud": "above" if price > cloud_top else ("below" if price < cloud_bottom else "inside"),
            "cloud_color": "bullish" if cloud_bullish else "bearish",
            "tk_cross": "bullish" if tk_bullish else "bearish",
            "confirmations": confirmations
        }
    )
