"""
Support and Resistance level identification.
Uses local extrema detection and clustering.
"""
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from ...models.technical import SupportResistanceResult


def calculate_support_resistance(
    df: pd.DataFrame,
    order: int = 10,
    proximity_pct: float = 0.01,
    max_levels: int = 5
) -> SupportResistanceResult:
    """
    Identify support and resistance levels from OHLCV data.

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        order: Window size for local extrema detection
        proximity_pct: Cluster levels within this % of price (default 1%)
        max_levels: Maximum number of levels to return per type

    Returns:
        SupportResistanceResult with support and resistance levels
    """
    if len(df) < order * 2 + 1:
        raise ValueError(f"Insufficient data for S/R calculation (need at least {order * 2 + 1} bars)")

    df = df.copy().reset_index(drop=True)
    current_price = df['close'].iloc[-1]

    # Find local minima (potential support)
    local_min_idx = argrelextrema(df['low'].values, np.less_equal, order=order)[0]
    support_prices = df['low'].iloc[local_min_idx].values

    # Find local maxima (potential resistance)
    local_max_idx = argrelextrema(df['high'].values, np.greater_equal, order=order)[0]
    resistance_prices = df['high'].iloc[local_max_idx].values

    # Cluster nearby levels
    support_levels = _cluster_levels(support_prices, proximity_pct)
    resistance_levels = _cluster_levels(resistance_prices, proximity_pct)

    # Filter: support below current price, resistance above
    support_levels = [level for level in support_levels if level < current_price]
    resistance_levels = [level for level in resistance_levels if level > current_price]

    # Sort and limit
    # Support: highest levels first (closest to current price)
    support_levels = sorted(support_levels, reverse=True)[:max_levels]

    # Resistance: lowest levels first (closest to current price)
    resistance_levels = sorted(resistance_levels)[:max_levels]

    return SupportResistanceResult(
        support_levels=support_levels,
        resistance_levels=resistance_levels
    )


def _cluster_levels(prices: np.ndarray, proximity_pct: float) -> list[float]:
    """
    Cluster nearby price levels.

    Groups prices that are within proximity_pct of each other,
    then returns the average of each cluster.

    Args:
        prices: Array of price levels
        proximity_pct: Cluster threshold as percentage (e.g., 0.01 = 1%)

    Returns:
        List of clustered price levels
    """
    if len(prices) == 0:
        return []

    # Sort prices
    sorted_prices = np.sort(prices)

    clusters = []
    current_cluster = [sorted_prices[0]]

    for price in sorted_prices[1:]:
        # Check if price is within proximity_pct of cluster mean
        cluster_mean = np.mean(current_cluster)
        threshold = cluster_mean * proximity_pct

        if abs(price - cluster_mean) <= threshold:
            # Add to current cluster
            current_cluster.append(price)
        else:
            # Start new cluster
            clusters.append(np.mean(current_cluster))
            current_cluster = [price]

    # Add final cluster
    if current_cluster:
        clusters.append(np.mean(current_cluster))

    return clusters
