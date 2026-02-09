"""
Convergence scoring across all technical analysis methods.
Analyzes agreement between different indicators.
"""
from typing import Dict
from collections import Counter
from ...models.technical import ConvergenceResult, TASignal


def calculate_convergence(
    rsi_signal: TASignal,
    macd_signal: TASignal,
    bollinger_signal: TASignal,
    ichimoku_signal: TASignal,
    volume_profile_signal: TASignal = None,
    sr_signal: TASignal = None
) -> ConvergenceResult:
    """
    Calculate convergence score across all TA methods.

    Args:
        rsi_signal: RSI signal
        macd_signal: MACD signal
        bollinger_signal: Bollinger Bands signal
        ichimoku_signal: Ichimoku Cloud signal
        volume_profile_signal: Optional Volume Profile signal
        sr_signal: Optional Support/Resistance signal

    Returns:
        ConvergenceResult with overall direction, confidence, and agreement metrics
    """
    # Collect all signals
    method_signals = {
        "rsi": rsi_signal,
        "macd": macd_signal,
        "bollinger": bollinger_signal,
        "ichimoku": ichimoku_signal
    }

    # Add optional signals if provided
    if volume_profile_signal:
        method_signals["volume_profile"] = volume_profile_signal
    if sr_signal:
        method_signals["support_resistance"] = sr_signal

    # Count direction votes
    direction_votes = [signal.direction for signal in method_signals.values()]
    direction_counts = Counter(direction_votes)
    total_methods = len(method_signals)

    # Determine overall direction (majority vote)
    # If tie between bullish and bearish, result is neutral
    most_common = direction_counts.most_common(2)

    if len(most_common) == 1:
        # All methods agree
        overall_direction = most_common[0][0]
        agreeing_methods = most_common[0][1]
    elif most_common[0][1] > most_common[1][1]:
        # Clear majority
        overall_direction = most_common[0][0]
        agreeing_methods = most_common[0][1]
    else:
        # Tie between top two directions
        if "neutral" in [most_common[0][0], most_common[1][0]]:
            # If one of the tied is neutral, use the other
            overall_direction = most_common[0][0] if most_common[0][0] != "neutral" else most_common[1][0]
            agreeing_methods = most_common[0][1]
        else:
            # Tie between bullish and bearish -> neutral
            overall_direction = "neutral"
            agreeing_methods = direction_counts.get("neutral", 0)

    # Calculate base confidence (agreement ratio)
    base_confidence = agreeing_methods / total_methods

    # Weight by individual method confidences
    # Calculate weighted average confidence of agreeing methods
    agreeing_confidences = [
        signal.confidence
        for signal in method_signals.values()
        if signal.direction == overall_direction
    ]

    if agreeing_confidences:
        avg_agreeing_confidence = sum(agreeing_confidences) / len(agreeing_confidences)
    else:
        avg_agreeing_confidence = 0.5

    # Combine base confidence with method confidences
    weighted_confidence = (base_confidence + avg_agreeing_confidence) / 2

    # Apply convergence boost/penalty
    if agreeing_methods >= 4:
        # Strong convergence - boost confidence
        final_confidence = min(weighted_confidence * 1.2, 1.0)
    elif agreeing_methods <= 2:
        # Weak convergence - reduce confidence
        final_confidence = weighted_confidence * 0.7
    else:
        # Moderate convergence - no adjustment
        final_confidence = weighted_confidence

    # Ensure confidence is in valid range
    final_confidence = max(0.0, min(1.0, final_confidence))

    return ConvergenceResult(
        overall_direction=overall_direction,
        confidence=final_confidence,
        agreeing_methods=agreeing_methods,
        total_methods=total_methods,
        method_signals=method_signals
    )
