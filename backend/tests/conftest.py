"""Shared fixtures for FinSpeak Trader tests."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    """Generate realistic OHLCV data (~180 days of AAPL-like prices)."""
    np.random.seed(42)
    n = 180
    dates = pd.date_range(end="2026-02-06", periods=n, freq="B")  # Feb 6 = Friday

    # Simulate price walk starting at ~180
    base_price = 180.0
    returns = np.random.normal(0.0005, 0.015, n)
    close_prices = base_price * np.cumprod(1 + returns)

    # Generate OHLCV from close prices
    high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.008, n)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.008, n)))
    open_prices = close_prices * (1 + np.random.normal(0, 0.005, n))
    volumes = np.random.uniform(30_000_000, 90_000_000, n)

    # Ensure high >= max(open, close) and low <= min(open, close)
    high_prices = np.maximum(high_prices, np.maximum(open_prices, close_prices))
    low_prices = np.minimum(low_prices, np.minimum(open_prices, close_prices))

    return pd.DataFrame({
        "date": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volumes,
    })


@pytest.fixture
def short_ohlcv() -> pd.DataFrame:
    """Very short OHLCV data (5 rows) for edge case testing."""
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=5, freq="B"),
        "open": [100.0, 101.0, 99.0, 102.0, 100.5],
        "high": [102.0, 103.0, 101.0, 104.0, 102.5],
        "low": [99.0, 100.0, 98.0, 101.0, 99.5],
        "close": [101.0, 99.5, 100.5, 103.0, 101.0],
        "volume": [50e6, 45e6, 60e6, 55e6, 48e6],
    })
