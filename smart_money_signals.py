from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List
import pandas as pd

from config import (
    ENABLE_PUMP_DUMP_DETECTION,
    PUMP_DETECTION_PERIOD_MINUTES,
    PUMP_THRESHOLD_PERCENT,
    DUMP_DETECTION_PERIOD_MINUTES,
    DUMP_THRESHOLD_PERCENT,
    WEIGHT_VOLUME,
    MIN_SIGNAL_STRENGTH,
)
from whale_tracker import WhaleSignal

logger = logging.getLogger(__name__)


@dataclass
class SmartMoneySignal:
    """Composite signal from smart money (whale + exchange flow + on-chain)"""
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    whale_signal: float  # -10 to +10
    exchange_flow_signal: float  # -10 to +10
    on_chain_signal: float  # -10 to +10
    total_score: float  # composite
    is_pump_detected: bool = False
    is_dump_detected: bool = False
    reasons: List[str] = field(default_factory=list)


class SmartMoneyAnalyzer:
    """Analyze smart money and on-chain signals for trading"""

    def __init__(self):
        self.price_history = []
        self.volume_history = []

    def analyze_smart_money(self, whale_signal: WhaleSignal, df_candles: pd.DataFrame) -> SmartMoneySignal:
        """
        Combine whale tracking, exchange flows, and technical indicators
        to generate a composite smart money signal.
        """
        if df_candles.empty:
            return SmartMoneySignal(
                action="HOLD",
                confidence=0.0,
                whale_signal=0.0,
                exchange_flow_signal=0.0,
                on_chain_signal=0.0,
                total_score=0.0,
                reasons=["No candle data available"],
            )

        close = df_candles["close"].astype(float)
        volume = df_candles["volume"].astype(float)
        high = df_candles["high"].astype(float)
        low = df_candles["low"].astype(float)

        current_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price
        price_change_percent = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0

        # Calculate individual signals
        whale_score = whale_signal.whale_score
        exchange_score = whale_signal.exchange_flow_score
        on_chain_score = self._calculate_on_chain_signal(close, volume)

        # Detect pump/dump
        is_pump = self._detect_pump(price_change_percent, high, low, close)
        is_dump = self._detect_dump(price_change_percent, high, low, close)

        # Composite score
        total_score = (
            whale_score +
            exchange_score +
            on_chain_score
        )

        # Generate action
        if total_score > 5.0 and not is_dump:
            action = "BUY"
            confidence = min(0.95, abs(total_score) / 15.0)
        elif total_score < -5.0 and not is_pump:
            action = "SELL"
            confidence = min(0.95, abs(total_score) / 15.0)
        else:
            action = "HOLD"
            confidence = 0.0

        reasons = whale_signal.reasons.copy()
        if is_pump:
            reasons.append(f"PUMP DETECTED: {abs(price_change_percent):.2f}% in {PUMP_DETECTION_PERIOD_MINUTES}m")
        if is_dump:
            reasons.append(f"DUMP DETECTED: {abs(price_change_percent):.2f}% in {DUMP_DETECTION_PERIOD_MINUTES}m")

        return SmartMoneySignal(
            action=action,
            confidence=confidence,
            whale_signal=whale_score,
            exchange_flow_signal=exchange_score,
            on_chain_signal=on_chain_score,
            total_score=total_score,
            is_pump_detected=is_pump,
            is_dump_detected=is_dump,
            reasons=reasons,
        )

    def _calculate_on_chain_signal(self, close: pd.Series, volume: pd.Series) -> float:
        """
        Calculate on-chain signal based on volume analysis.
        (In production, this would include actual on-chain data from Etherscan, etc.)
        """
        if len(close) < 20:
            return 0.0

        # Volume spike detection
        avg_volume = volume.iloc[-20:].mean()
        current_volume = volume.iloc[-1]
        volume_multiplier = current_volume / avg_volume if avg_volume > 0 else 1.0

        # Price momentum
        price_momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] if close.iloc[-5] > 0 else 0

        # Score based on volume confirmation
        on_chain_score = 0.0
        if volume_multiplier > 1.5:  # High volume
            if price_momentum > 0:
                on_chain_score = 2.0
            else:
                on_chain_score = -1.5
        elif volume_multiplier < 0.7:  # Low volume
            if price_momentum > 0:
                on_chain_score = 0.5
            else:
                on_chain_score = -0.5

        return on_chain_score

    def _detect_pump(self, price_change_percent: float, high: pd.Series, low: pd.Series, close: pd.Series) -> bool:
        """
        Detect pump scenarios: rapid price increase
        """
        if not ENABLE_PUMP_DUMP_DETECTION:
            return False

        return abs(price_change_percent) > PUMP_THRESHOLD_PERCENT

    def _detect_dump(self, price_change_percent: float, high: pd.Series, low: pd.Series, close: pd.Series) -> bool:
        """
        Detect dump scenarios: rapid price decrease
        """
        if not ENABLE_PUMP_DUMP_DETECTION:
            return False

        return price_change_percent < -DUMP_THRESHOLD_PERCENT

    def get_smart_money_confidence(self, score: float, max_score: float = 15.0) -> float:
        """
        Convert raw score to confidence between 0.0 and 1.0
        """
        return max(0.0, min(1.0, abs(score) / max_score))
