"""
Pydantic models for Technical Analysis results.
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class TASignal(BaseModel):
    """Generic technical analysis signal."""
    direction: Literal["bullish", "neutral", "bearish"]
    confidence: float = Field(ge=0.0, le=1.0)
    details: dict = Field(default_factory=dict)


class VolumeProfileResult(BaseModel):
    """Volume Profile analysis result."""
    vpoc: float = Field(description="Volume Point of Control - price with highest volume")
    vah: float = Field(description="Value Area High - top of 70% volume zone")
    val: float = Field(description="Value Area Low - bottom of 70% volume zone")
    value_area_pct: float = Field(description="Percentage of volume in value area")
    note: str = "Estimated from daily data"


class SupportResistanceResult(BaseModel):
    """Support and Resistance levels."""
    support_levels: list[float] = Field(description="Support levels below current price")
    resistance_levels: list[float] = Field(description="Resistance levels above current price")


class RSIResult(BaseModel):
    """RSI (Relative Strength Index) result."""
    current_value: float = Field(description="Current RSI value (0-100)")
    signal: TASignal


class MACDResult(BaseModel):
    """MACD (Moving Average Convergence Divergence) result."""
    macd_line: float = Field(description="MACD line value")
    signal_line: float = Field(description="Signal line value")
    histogram: float = Field(description="MACD histogram (MACD - Signal)")
    signal: TASignal


class BollingerResult(BaseModel):
    """Bollinger Bands result."""
    upper: float = Field(description="Upper band")
    middle: float = Field(description="Middle band (SMA)")
    lower: float = Field(description="Lower band")
    bandwidth: float = Field(description="Band width normalized")
    squeeze: bool = Field(description="True if bandwidth indicates squeeze")
    signal: TASignal


class IchimokuResult(BaseModel):
    """Ichimoku Cloud result."""
    tenkan_sen: float = Field(description="Conversion line")
    kijun_sen: float = Field(description="Base line")
    senkou_span_a: float = Field(description="Leading Span A")
    senkou_span_b: float = Field(description="Leading Span B")
    chikou_span: float = Field(description="Lagging Span")
    signal: TASignal


class ConvergenceResult(BaseModel):
    """Convergence analysis across all TA methods."""
    overall_direction: Literal["bullish", "neutral", "bearish"]
    confidence: float = Field(ge=0.0, le=1.0, description="Higher when more methods agree")
    agreeing_methods: int = Field(description="Number of methods agreeing with overall direction")
    total_methods: int = Field(description="Total number of methods analyzed")
    method_signals: dict[str, TASignal]


class TechnicalAnalysisBundle(BaseModel):
    """Complete technical analysis bundle for a ticker."""
    ticker: str
    timestamp: datetime
    volume_profile: VolumeProfileResult
    support_resistance: SupportResistanceResult
    rsi: RSIResult
    macd: MACDResult
    bollinger: BollingerResult
    ichimoku: IchimokuResult
    convergence: ConvergenceResult
