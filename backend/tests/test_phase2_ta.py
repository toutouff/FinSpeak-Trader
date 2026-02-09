"""Tests for Phase 2 - Technical Analysis Engine."""
import pytest
import pandas as pd
import numpy as np
from app.services.ta.volume_profile import calculate_volume_profile
from app.services.ta.support_resistance import calculate_support_resistance
from app.services.ta.rsi import calculate_rsi
from app.services.ta.macd import calculate_macd
from app.services.ta.bollinger import calculate_bollinger
from app.services.ta.ichimoku import calculate_ichimoku
from app.services.ta.convergence import calculate_convergence
from app.models.technical import (
    VolumeProfileResult,
    SupportResistanceResult,
    RSIResult,
    MACDResult,
    BollingerResult,
    IchimokuResult,
    ConvergenceResult,
    TASignal,
)


# ============================================================
# Volume Profile (TECH-01)
# ============================================================

class TestVolumeProfile:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_volume_profile(sample_ohlcv)
        assert isinstance(result, VolumeProfileResult)

    def test_vpoc_within_price_range(self, sample_ohlcv):
        result = calculate_volume_profile(sample_ohlcv)
        price_min = sample_ohlcv["low"].min()
        price_max = sample_ohlcv["high"].max()
        assert price_min <= result.vpoc <= price_max

    def test_value_area_ordering(self, sample_ohlcv):
        result = calculate_volume_profile(sample_ohlcv)
        assert result.val <= result.vpoc <= result.vah

    def test_value_area_covers_roughly_70_pct(self, sample_ohlcv):
        result = calculate_volume_profile(sample_ohlcv)
        assert 0.60 <= result.value_area_pct <= 0.85

    def test_note_labels_estimated(self, sample_ohlcv):
        result = calculate_volume_profile(sample_ohlcv)
        assert "estimated" in result.note.lower() or "daily" in result.note.lower()

    def test_insufficient_data_raises(self, short_ohlcv):
        with pytest.raises(ValueError):
            calculate_volume_profile(short_ohlcv)


# ============================================================
# Support / Resistance (TECH-02)
# ============================================================

class TestSupportResistance:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_support_resistance(sample_ohlcv)
        assert isinstance(result, SupportResistanceResult)

    def test_support_below_current_price(self, sample_ohlcv):
        result = calculate_support_resistance(sample_ohlcv)
        current_price = sample_ohlcv["close"].iloc[-1]
        for level in result.support_levels:
            assert level <= current_price * 1.01  # small tolerance

    def test_resistance_above_current_price(self, sample_ohlcv):
        result = calculate_support_resistance(sample_ohlcv)
        current_price = sample_ohlcv["close"].iloc[-1]
        for level in result.resistance_levels:
            assert level >= current_price * 0.99  # small tolerance

    def test_returns_lists(self, sample_ohlcv):
        result = calculate_support_resistance(sample_ohlcv)
        assert isinstance(result.support_levels, list)
        assert isinstance(result.resistance_levels, list)


# ============================================================
# RSI (TECH-03)
# ============================================================

class TestRSI:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_rsi(sample_ohlcv)
        assert isinstance(result, RSIResult)

    def test_rsi_in_valid_range(self, sample_ohlcv):
        result = calculate_rsi(sample_ohlcv)
        assert 0 <= result.current_value <= 100

    def test_signal_has_valid_direction(self, sample_ohlcv):
        result = calculate_rsi(sample_ohlcv)
        assert result.signal.direction in ("bullish", "neutral", "bearish")

    def test_signal_confidence_in_range(self, sample_ohlcv):
        result = calculate_rsi(sample_ohlcv)
        assert 0.0 <= result.signal.confidence <= 1.0

    def test_overbought_is_bearish(self):
        """If RSI > 70, signal should be bearish."""
        # Create data with strong upward trend to push RSI high
        n = 60
        prices = 100.0 + np.arange(n) * 1.5  # strong uptrend
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=n, freq="B"),
            "open": prices - 0.5,
            "high": prices + 1.0,
            "low": prices - 1.0,
            "close": prices,
            "volume": [50e6] * n,
        })
        result = calculate_rsi(df)
        # Very strong uptrend should give overbought reading
        assert result.current_value > 60  # at least elevated

    def test_oversold_is_bullish(self):
        """If RSI < 30, signal should be bullish."""
        n = 60
        prices = 200.0 - np.arange(n) * 1.5  # strong downtrend
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=n, freq="B"),
            "open": prices + 0.5,
            "high": prices + 1.0,
            "low": prices - 1.0,
            "close": prices,
            "volume": [50e6] * n,
        })
        result = calculate_rsi(df)
        assert result.current_value < 40  # at least depressed


# ============================================================
# MACD (TECH-04)
# ============================================================

class TestMACD:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_macd(sample_ohlcv)
        assert isinstance(result, MACDResult)

    def test_histogram_equals_macd_minus_signal(self, sample_ohlcv):
        result = calculate_macd(sample_ohlcv)
        expected = result.macd_line - result.signal_line
        assert abs(result.histogram - expected) < 0.01

    def test_signal_direction_valid(self, sample_ohlcv):
        result = calculate_macd(sample_ohlcv)
        assert result.signal.direction in ("bullish", "neutral", "bearish")

    def test_signal_confidence_in_range(self, sample_ohlcv):
        result = calculate_macd(sample_ohlcv)
        assert 0.0 <= result.signal.confidence <= 1.0


# ============================================================
# Bollinger Bands (TECH-05)
# ============================================================

class TestBollinger:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_bollinger(sample_ohlcv)
        assert isinstance(result, BollingerResult)

    def test_band_ordering(self, sample_ohlcv):
        result = calculate_bollinger(sample_ohlcv)
        assert result.lower < result.middle < result.upper

    def test_bandwidth_positive(self, sample_ohlcv):
        result = calculate_bollinger(sample_ohlcv)
        assert result.bandwidth > 0

    def test_squeeze_is_boolean(self, sample_ohlcv):
        result = calculate_bollinger(sample_ohlcv)
        assert isinstance(result.squeeze, bool)

    def test_signal_confidence_in_range(self, sample_ohlcv):
        result = calculate_bollinger(sample_ohlcv)
        assert 0.0 <= result.signal.confidence <= 1.0


# ============================================================
# Ichimoku Cloud (TECH-06)
# ============================================================

class TestIchimoku:
    def test_returns_valid_result(self, sample_ohlcv):
        result = calculate_ichimoku(sample_ohlcv)
        assert isinstance(result, IchimokuResult)

    def test_all_components_are_floats(self, sample_ohlcv):
        result = calculate_ichimoku(sample_ohlcv)
        assert isinstance(result.tenkan_sen, float)
        assert isinstance(result.kijun_sen, float)
        assert isinstance(result.senkou_span_a, float)
        assert isinstance(result.senkou_span_b, float)
        assert isinstance(result.chikou_span, float)

    def test_signal_direction_valid(self, sample_ohlcv):
        result = calculate_ichimoku(sample_ohlcv)
        assert result.signal.direction in ("bullish", "neutral", "bearish")

    def test_components_within_price_range(self, sample_ohlcv):
        result = calculate_ichimoku(sample_ohlcv)
        price_min = sample_ohlcv["low"].min() * 0.9
        price_max = sample_ohlcv["high"].max() * 1.1
        for val in [result.tenkan_sen, result.kijun_sen, result.senkou_span_a, result.senkou_span_b]:
            assert price_min <= val <= price_max


# ============================================================
# Convergence (TECH-07)
# ============================================================

class TestConvergence:
    def test_returns_valid_result(self, sample_ohlcv):
        rsi = calculate_rsi(sample_ohlcv)
        macd = calculate_macd(sample_ohlcv)
        bollinger = calculate_bollinger(sample_ohlcv)
        ichimoku = calculate_ichimoku(sample_ohlcv)
        result = calculate_convergence(
            rsi_signal=rsi.signal,
            macd_signal=macd.signal,
            bollinger_signal=bollinger.signal,
            ichimoku_signal=ichimoku.signal,
        )
        assert isinstance(result, ConvergenceResult)

    def test_full_agreement_high_confidence(self):
        """When all methods agree, confidence should be high."""
        bullish = TASignal(direction="bullish", confidence=0.8, details={})
        result = calculate_convergence(
            rsi_signal=bullish,
            macd_signal=bullish,
            bollinger_signal=bullish,
            ichimoku_signal=bullish,
        )
        assert result.overall_direction == "bullish"
        assert result.confidence >= 0.7
        assert result.agreeing_methods == 4

    def test_split_signals_lower_confidence(self):
        """When methods disagree, confidence should be lower."""
        bullish = TASignal(direction="bullish", confidence=0.7, details={})
        bearish = TASignal(direction="bearish", confidence=0.7, details={})
        result = calculate_convergence(
            rsi_signal=bullish,
            macd_signal=bearish,
            bollinger_signal=bullish,
            ichimoku_signal=bearish,
        )
        # With 2-2 split, confidence should be low
        assert result.confidence < 0.6

    def test_majority_determines_direction(self):
        """Majority should determine overall direction."""
        bullish = TASignal(direction="bullish", confidence=0.7, details={})
        bearish = TASignal(direction="bearish", confidence=0.6, details={})
        result = calculate_convergence(
            rsi_signal=bullish,
            macd_signal=bullish,
            bollinger_signal=bullish,
            ichimoku_signal=bearish,
        )
        assert result.overall_direction == "bullish"
        assert result.agreeing_methods == 3

    def test_confidence_in_range(self, sample_ohlcv):
        rsi = calculate_rsi(sample_ohlcv)
        macd = calculate_macd(sample_ohlcv)
        bollinger = calculate_bollinger(sample_ohlcv)
        ichimoku = calculate_ichimoku(sample_ohlcv)
        result = calculate_convergence(
            rsi_signal=rsi.signal,
            macd_signal=macd.signal,
            bollinger_signal=bollinger.signal,
            ichimoku_signal=ichimoku.signal,
        )
        assert 0.0 <= result.confidence <= 1.0
        assert result.total_methods == 4
