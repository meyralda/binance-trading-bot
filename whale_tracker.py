from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests

from config import (
    BINANCE_WALLETS,
    COINBASE_WALLETS,
    KRAKEN_WALLETS,
    BYBIT_WALLETS,
    HUOBI_WALLETS,
    OKEX_WALLETS,
    GATE_WALLETS,
    WHALE_WALLETS,
    WHALE_LABELS,
    WHALE_MINIMUM_TRANSACTION_USDT,
    WHALE_BUY_WEIGHT,
    WHALE_SELL_WEIGHT,
    WHALE_ACCUMULATION_THRESHOLD,
    WHALE_DISTRIBUTION_THRESHOLD,
    WHALE_SIGNAL_LOOKBACK_HOURS,
    EXCHANGE_INFLOW_SENSITIVITY,
    EXCHANGE_OUTFLOW_SENSITIVITY,
    ENABLE_WHALE_TRACKING,
    MONITOR_WHALE_MOVEMENTS,
    DETECT_PROFIT_TAKING,
    DETECT_LOSS_REALIZATION,
    LARGE_MOVEMENT_THRESHOLD_PERCENT,
)

logger = logging.getLogger(__name__)


@dataclass
class WhaleTransaction:
    """Represents a large whale transaction"""
    wallet_address: str
    wallet_label: str
    transaction_hash: str
    timestamp: datetime
    from_address: str
    to_address: str
    amount: float
    value_usd: float
    token: str
    direction: str  # "IN" or "OUT"
    transaction_type: str  # "BUY", "SELL", "TRANSFER", "DEPOSIT", "WITHDRAWAL"


@dataclass
class WhaleSignal:
    """Composite signal from whale activity"""
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    whale_score: float  # composite score from all whales
    exchange_flow_score: float
    reasons: List[str] = field(default_factory=list)
    transaction_count: int = 0
    total_volume_usd: float = 0.0
    active_whales: List[str] = field(default_factory=list)


class WhaleTracker:
    """Monitor whale wallets and exchange flows for trading signals"""

    def __init__(self):
        self.exchange_wallets = {
            "binance": BINANCE_WALLETS or [],
            "coinbase": COINBASE_WALLETS or [],
            "kraken": KRAKEN_WALLETS or [],
            "bybit": BYBIT_WALLETS or [],
            "huobi": HUOBI_WALLETS or [],
            "okex": OKEX_WALLETS or [],
            "gate.io": GATE_WALLETS or [],
        }
        self.whale_wallets = WHALE_WALLETS or []
        self.whale_labels = WHALE_LABELS or []
        self.transaction_history: List[WhaleTransaction] = []
        self.last_update = None

    def track_whale_activity(self, symbol: str, hours_lookback: int = None) -> WhaleSignal:
        """
        Analyze whale wallet activity for the given symbol.
        Returns a composite signal based on whale movements.
        """
        if not ENABLE_WHALE_TRACKING:
            return WhaleSignal(
                action="HOLD",
                confidence=0.0,
                whale_score=0.0,
                exchange_flow_score=0.0,
                reasons=["Whale tracking disabled"],
            )

        hours = hours_lookback or WHALE_SIGNAL_LOOKBACK_HOURS
        lookback_time = datetime.utcnow() - timedelta(hours=hours)

        whale_buys = []
        whale_sells = []
        exchange_inflows = []
        exchange_outflows = []

        # Fetch and categorize transactions
        for tx in self.transaction_history:
            if tx.timestamp < lookback_time:
                continue

            # Check if from whale or exchange wallet
            if tx.wallet_address in self.whale_wallets:
                if tx.direction == "OUT" and tx.value_usd >= WHALE_MINIMUM_TRANSACTION_USDT:
                    whale_sells.append(tx)
                elif tx.direction == "IN" and tx.value_usd >= WHALE_MINIMUM_TRANSACTION_USDT:
                    whale_buys.append(tx)

            # Check exchange flows
            for exchange_name, wallets in self.exchange_wallets.items():
                if tx.wallet_address in wallets:
                    if tx.direction == "IN":  # Money coming to exchange = selling pressure
                        exchange_inflows.append(tx)
                    elif tx.direction == "OUT":  # Money leaving exchange = buying pressure
                        exchange_outflows.append(tx)

        # Calculate scores
        whale_score = self._calculate_whale_score(whale_buys, whale_sells)
        exchange_flow_score = self._calculate_exchange_flow_score(exchange_inflows, exchange_outflows)

        # Combine signals
        composite_score = whale_score + exchange_flow_score
        action, confidence = self._generate_action(composite_score, whale_buys, whale_sells)

        active_whales = list(set([tx.wallet_label for tx in whale_buys + whale_sells]))
        total_volume = sum(tx.value_usd for tx in whale_buys + whale_sells)
        tx_count = len(whale_buys) + len(whale_sells)

        reasons = []
        if whale_buys:
            reasons.append(f"Whale accumulation: {len(whale_buys)} buy transactions")
        if whale_sells:
            reasons.append(f"Whale distribution: {len(whale_sells)} sell transactions")
        if exchange_inflows:
            reasons.append(f"Exchange inflows: {len(exchange_inflows)} deposits (bearish)")
        if exchange_outflows:
            reasons.append(f"Exchange outflows: {len(exchange_outflows)} withdrawals (bullish)")

        return WhaleSignal(
            action=action,
            confidence=confidence,
            whale_score=whale_score,
            exchange_flow_score=exchange_flow_score,
            reasons=reasons,
            transaction_count=tx_count,
            total_volume_usd=total_volume,
            active_whales=active_whales,
        )

    def _calculate_whale_score(self, buys: List[WhaleTransaction], sells: List[WhaleTransaction]) -> float:
        """
        Calculate whale sentiment score.
        Positive = accumulation (bullish), Negative = distribution (bearish)
        """
        buy_volume = sum(tx.value_usd for tx in buys)
        sell_volume = sum(tx.value_usd for tx in sells)
        buy_count = len(buys)
        sell_count = len(sells)

        # Weighted score: volume + transaction count
        buy_score = (buy_volume / WHALE_MINIMUM_TRANSACTION_USDT) * WHALE_BUY_WEIGHT if buy_volume > 0 else 0
        sell_score = (sell_volume / WHALE_MINIMUM_TRANSACTION_USDT) * WHALE_SELL_WEIGHT if sell_volume > 0 else 0

        # Add transaction count bonus
        if buy_count >= WHALE_ACCUMULATION_THRESHOLD:
            buy_score += 1.0
        if sell_count >= WHALE_DISTRIBUTION_THRESHOLD:
            sell_score += 1.0

        return buy_score - sell_score

    def _calculate_exchange_flow_score(self, inflows: List[WhaleTransaction], outflows: List[WhaleTransaction]) -> float:
        """
        Calculate exchange flow sentiment.
        Positive = outflows (bullish, money leaving exchange), Negative = inflows (bearish, selling pressure)
        """
        inflow_volume = sum(tx.value_usd for tx in inflows)
        outflow_volume = sum(tx.value_usd for tx in outflows)

        outflow_score = (outflow_volume / WHALE_MINIMUM_TRANSACTION_USDT) * EXCHANGE_OUTFLOW_SENSITIVITY if outflow_volume > 0 else 0
        inflow_score = (inflow_volume / WHALE_MINIMUM_TRANSACTION_USDT) * EXCHANGE_INFLOW_SENSITIVITY if inflow_volume > 0 else 0

        return outflow_score - inflow_score

    def _generate_action(self, composite_score: float, buys: List[WhaleTransaction], sells: List[WhaleTransaction]) -> Tuple[str, float]:
        """
        Generate trading action from composite whale score.
        """
        if composite_score > 3.0:
            return "BUY", min(0.95, abs(composite_score) / 10.0)
        elif composite_score < -3.0:
            return "SELL", min(0.95, abs(composite_score) / 10.0)
        else:
            return "HOLD", 0.0

    def detect_pump_dump(self, price_change_percent: float, time_window_minutes: int = 30) -> Tuple[bool, str]:
        """
        Detect potential pump & dump schemes based on price movements and whale activity.
        Returns (is_pump_dump, reason)
        """
        recent_txs = [
            tx for tx in self.transaction_history
            if (datetime.utcnow() - tx.timestamp).total_seconds() < time_window_minutes * 60
        ]

        if not recent_txs:
            return False, "No recent whale activity"

        # Check for sudden large movements with whale activity
        if abs(price_change_percent) > LARGE_MOVEMENT_THRESHOLD_PERCENT:
            recent_distribution = sum(1 for tx in recent_txs if tx.direction == "OUT")
            recent_accumulation = sum(1 for tx in recent_txs if tx.direction == "IN")

            if price_change_percent > 0 and recent_accumulation > recent_distribution:
                return False, f"Organic buying pressure ({recent_accumulation} accumulation)"
            elif price_change_percent < 0 and recent_distribution > recent_accumulation:
                return False, f"Organic selling pressure ({recent_distribution} distribution)"

            # Suspicious: high price change with mismatched whale activity
            return True, f"Suspicious movement: {abs(price_change_percent):.2f}% with whale misalignment"

        return False, "Normal activity"

    def detect_profit_taking(self, current_price: float, highest_recent_price: float) -> bool:
        """
        Detect if whales are taking profits at resistance levels.
        """
        if not DETECT_PROFIT_TAKING or highest_recent_price == 0:
            return False

        price_drop_percent = ((highest_recent_price - current_price) / highest_recent_price) * 100

        # Check for recent whale sells
        recent_sells = [
            tx for tx in self.transaction_history
            if tx.direction == "OUT" and
               (datetime.utcnow() - tx.timestamp).total_seconds() < 3600  # last hour
        ]

        return len(recent_sells) > 0 and price_drop_percent > 0

    def detect_loss_realization(self, current_price: float, lowest_recent_price: float) -> bool:
        """
        Detect if whales are realizing losses at support levels.
        """
        if not DETECT_LOSS_REALIZATION or lowest_recent_price == 0:
            return False

        price_increase_percent = ((current_price - lowest_recent_price) / lowest_recent_price) * 100

        # Check for recent whale buys
        recent_buys = [
            tx for tx in self.transaction_history
            if tx.direction == "IN" and
               (datetime.utcnow() - tx.timestamp).total_seconds() < 3600  # last hour
        ]

        return len(recent_buys) > 0 and price_increase_percent > 0

    def add_transaction(self, tx: WhaleTransaction) -> None:
        """Add a transaction to the tracking history"""
        self.transaction_history.append(tx)
        # Keep only recent history to save memory
        self.transaction_history = self.transaction_history[-10000:]

    def get_whale_summary(self) -> Dict:
        """Get summary of whale activity"""
        if not self.transaction_history:
            return {"total_whales": 0, "total_transactions": 0, "total_volume_usd": 0.0}

        return {
            "total_whales": len(set(tx.wallet_address for tx in self.transaction_history)),
            "total_transactions": len(self.transaction_history),
            "total_volume_usd": sum(tx.value_usd for tx in self.transaction_history),
            "last_update": self.last_update,
        }
