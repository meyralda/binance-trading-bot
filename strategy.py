from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TradePlan:
    action: str
    confidence: float
    reasons: List[str]
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: float
    estimated_value_usdt: float


def calculate_position_size(balance_usdt: float, risk_per_trade_pct: float, entry_price: float, stop_loss_price: float) -> float:
    """Calculate the trade size as a function of the allowed risk budget and stop level."""
    if balance_usdt <= 0 or entry_price <= 0 or stop_loss_price <= 0:
        return 0.0

    risk_budget = balance_usdt * (risk_per_trade_pct / 100.0)
    distance = abs(entry_price - stop_loss_price) / entry_price

    if distance <= 0:
        return 0.0

    return risk_budget / distance


def calculate_order_quantity(balance_usdt: float, risk_per_trade_pct: float, entry_price: float, stop_loss_price: float) -> float:
    qty = calculate_position_size(balance_usdt, risk_per_trade_pct, entry_price, stop_loss_price)
    return max(0.0, qty)


def build_trade_plan(signal, balance_usdt: float, risk_per_trade_pct: float) -> TradePlan:
    if signal.action == "HOLD":
        raise ValueError("Cannot build trade plan for HOLD signal")

    entry_price = signal.entry_price
    stop_loss = signal.stop_loss
    take_profit = signal.take_profit
    quantity = calculate_order_quantity(balance_usdt, risk_per_trade_pct, entry_price, stop_loss)
    estimated_value_usdt = quantity * entry_price

    return TradePlan(
        action=signal.action,
        confidence=signal.confidence,
        reasons=signal.reasons,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        quantity=quantity,
        estimated_value_usdt=estimated_value_usdt,
    )
