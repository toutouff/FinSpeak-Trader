"""
Volume Profile calculation using daily OHLCV data.
Estimates volume distribution across price levels.
"""
import numpy as np
import pandas as pd
from ...models.technical import VolumeProfileResult


def calculate_volume_profile(
    df: pd.DataFrame,
    num_bins: int = 50
) -> VolumeProfileResult:
    """
    Calculate Volume Profile from OHLCV data.

    Uses triangular distribution weighted toward typical price ((H+L+C)/3)
    to estimate volume distribution across price levels.

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
        num_bins: Number of price bins for volume distribution

    Returns:
        VolumeProfileResult with VPOC, VAH, VAL
    """
    if len(df) < 10:
        raise ValueError("Insufficient data for volume profile calculation")

    # Calculate typical price for each bar
    df = df.copy()
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3

    # Determine price range
    price_min = df['low'].min()
    price_max = df['high'].max()

    # Create price bins
    bins = np.linspace(price_min, price_max, num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    # Initialize volume distribution array
    volume_dist = np.zeros(num_bins)

    # Distribute volume for each bar using triangular distribution
    for _, row in df.iterrows():
        bar_low = row['low']
        bar_high = row['high']
        bar_typical = row['typical_price']
        bar_volume = row['volume']

        if bar_volume == 0 or bar_high == bar_low:
            continue

        # Find bins that overlap with this bar's price range
        bin_mask = (bin_centers >= bar_low) & (bin_centers <= bar_high)
        overlapping_bins = np.where(bin_mask)[0]

        if len(overlapping_bins) == 0:
            # Bar falls between bins, assign to nearest
            nearest_bin = np.argmin(np.abs(bin_centers - bar_typical))
            volume_dist[nearest_bin] += bar_volume
        else:
            # Distribute volume using triangular weighting
            # Higher weight near typical price, lower near edges
            for bin_idx in overlapping_bins:
                bin_price = bin_centers[bin_idx]

                # Calculate triangular weight
                # Maximum at typical price, zero at edges
                if bin_price <= bar_typical:
                    # Rising edge
                    if bar_typical > bar_low:
                        weight = (bin_price - bar_low) / (bar_typical - bar_low)
                    else:
                        weight = 1.0
                else:
                    # Falling edge
                    if bar_high > bar_typical:
                        weight = (bar_high - bin_price) / (bar_high - bar_typical)
                    else:
                        weight = 1.0

                weight = max(0.0, min(1.0, weight))
                volume_dist[bin_idx] += bar_volume * weight

    # Normalize volume distribution
    total_volume = volume_dist.sum()
    if total_volume == 0:
        raise ValueError("No volume data available")

    volume_dist_pct = volume_dist / total_volume

    # Find VPOC (Volume Point of Control)
    vpoc_idx = np.argmax(volume_dist)
    vpoc = bin_centers[vpoc_idx]

    # Calculate Value Area (70% of volume centered on VPOC)
    # Start at VPOC and expand outward
    target_volume = 0.70
    value_area_volume = volume_dist_pct[vpoc_idx]
    lower_idx = vpoc_idx
    upper_idx = vpoc_idx

    while value_area_volume < target_volume:
        # Determine which direction to expand
        can_expand_lower = lower_idx > 0
        can_expand_upper = upper_idx < num_bins - 1

        if not can_expand_lower and not can_expand_upper:
            break

        lower_volume = volume_dist_pct[lower_idx - 1] if can_expand_lower else 0
        upper_volume = volume_dist_pct[upper_idx + 1] if can_expand_upper else 0

        # Expand toward higher volume
        if can_expand_lower and (not can_expand_upper or lower_volume >= upper_volume):
            lower_idx -= 1
            value_area_volume += volume_dist_pct[lower_idx]
        elif can_expand_upper:
            upper_idx += 1
            value_area_volume += volume_dist_pct[upper_idx]

    val = bin_centers[lower_idx]
    vah = bin_centers[upper_idx]

    return VolumeProfileResult(
        vpoc=float(vpoc),
        vah=float(vah),
        val=float(val),
        value_area_pct=float(value_area_volume),
        note="Estimated from daily data"
    )
