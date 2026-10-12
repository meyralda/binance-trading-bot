from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from config import (
    SYMBOL,
    BINANCE_WALLETS,
    COINBASE_WALLETS,
    KRAKEN_WALLETS,
    BYBIT_WALLETS,
    HUOBI_WALLETS,
    OKEX_WALLETS,
    GATE_WALLETS,
    MONITOR_EXCHANGE_INFLOWS,
    MONITOR_EXCHANGE_OUTFLOWS,
    EXCHANGE_FLOW_LOOKBACK_HOURS,
    WHALE_MINIMUM_TRANSACTION_USDT,
)

logger = logging.getLogger(__name__)


@dataclass
class ExchangeFlow:
    """Represents exchange wallet flows"""
    exchange_name: str
    wallet_address: str
    timestamp: datetime
    direction: str  # "IN" or "OUT"
    amount: float
    amount_usd: float
    token: str


@dataclass
class ExchangeFlowSignal:
    """Signal from exchange flow analysis"""
    total_inflows_usd: float = 0.0
    total_outflows_usd: float = 0.0
    net_flow_usd: float = 0.0  # positive = outflow (bullish), negative = inflow (bearish)
    inflow_count: int = 0
    outflow_count: int = 0
    exchanges_active: List[str] = field(default_factory=list)
    dominant_flow: str = "NEUTRAL"  # "INFLOW", "OUTFLOW", "NEUTRAL"
    severity: float = 0.0  # 0.0 to 1.0, how significant is the flow


class ExchangeMonitor:
    """Monitor exchange wallet flows for market signals"""

    EXCHANGE_WALLETS = {
        "binance": BINANCE_WALLETS or [],
        "coinbase": COINBASE_WALLETS or [],
        "kraken": KRAKEN_WALLETS or [],
        "bybit": BYBIT_WALLETS or [],
        "huobi": HUOBI_WALLETS or [],
        "okex": OKEX_WALLETS or [],
        "gate.io": GATE_WALLETS or [],
    }

    def __init__(self):
        self.flow_history: List[ExchangeFlow] = []
        self.last_analysis_time = None

    def analyze_exchange_flows(self, hours_lookback: int = None) -> ExchangeFlowSignal:
        """
        Analyze exchange inflows and outflows over the specified time window.
        """
        hours = hours_lookback or EXCHANGE_FLOW_LOOKBACK_HOURS
        lookback_time = datetime.utcnow() - timedelta(hours=hours)

        inflows = []
        outflows = []
        exchanges_active = set()

        for flow in self.flow_history:
            if flow.timestamp < lookback_time:
                continue
            if flow.amount_usd < WHALE_MINIMUM_TRANSACTION_USDT:
                continue

            exchanges_active.add(flow.exchange_name)

            if flow.direction == "IN":
                inflows.append(flow)
            elif flow.direction == "OUT":
                outflows.append(flow)

        total_inflow = sum(f.amount_usd for f in inflows)
        total_outflow = sum(f.amount_usd for f in outflows)
        net_flow = total_outflow - total_inflow  # positive = bullish, negative = bearish

        if total_outflow > total_inflow:
            dominant_flow = "OUTFLOW"
        elif total_inflow > total_outflow:
            dominant_flow = "INFLOW"
        else:
            dominant_flow = "NEUTRAL"

        # Calculate severity (0.0 to 1.0)
        total_flow = total_inflow + total_outflow
        severity = min(1.0, total_flow / (10 * WHALE_MINIMUM_TRANSACTION_USDT)) if total_flow > 0 else 0.0

        return ExchangeFlowSignal(
            total_inflows_usd=total_inflow,
            total_outflows_usd=total_outflow,
            net_flow_usd=net_flow,
            inflow_count=len(inflows),
            outflow_count=len(outflows),
            exchanges_active=list(exchanges_active),
            dominant_flow=dominant_flow,
            severity=severity,
        )

    def detect_exchange_accumulation(self) -> Tuple[bool, float]:
        """
        Detect if exchanges are accumulating coins (inflows).
        Returns (is_accumulating, score)
        """
        signal = self.analyze_exchange_flows(hours_lookback=24)
        is_accumulating = signal.dominant_flow == "INFLOW" and signal.severity > 0.5
        return is_accumulating, signal.severity

    def detect_exchange_distribution(self) -> Tuple[bool, float]:
        """
        Detect if exchanges are distributing coins (outflows).
        Returns (is_distributing, score)
        """
        signal = self.analyze_exchange_flows(hours_lookback=24)
        is_distributing = signal.dominant_flow == "OUTFLOW" and signal.severity > 0.5
        return is_distributing, signal.severity

    def add_flow(self, flow: ExchangeFlow) -> None:
        """Add a flow event to the history"""
        self.flow_history.append(flow)
        # Keep only recent history
        self.flow_history = self.flow_history[-5000:]

    def get_exchange_summary(self) -> Dict:
        """Get summary of exchange flows"""
        if not self.flow_history:
            return {"total_inflows": 0.0, "total_outflows": 0.0}

        return {
            "total_inflows_usd": sum(f.amount_usd for f in self.flow_history if f.direction == "IN"),
            "total_outflows_usd": sum(f.amount_usd for f in self.flow_history if f.direction == "OUT"),
            "total_flows": len(self.flow_history),
        }
