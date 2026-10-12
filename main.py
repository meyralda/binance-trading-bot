from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pandas as pd

from config import (
    EMA_FAST,
    EMA_SLOW,
    RSI_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    BOLLINGER_PERIOD,
    BOLLINGER_STD,
    ATR_PERIOD,
    SUPPORT_RESISTANCE_LOOKBACK,
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)
from indicators import atr, bollinger_bands, ema, macd, rsi, support_resistance, latest_signal_strength


@dataclass
class Signal:
    action: str
    confidence: float
    reasons: List[str] = field(default_factory=list)
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0


def generate_signal(df: pd.DataFrame) -> Signal:
    if df.empty or "close" not in df.columns:
        return Signal(action="HOLD", confidence=0.0, reasons=["No data available for signal generation"])

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    ema_fast = ema(close, EMA_FAST).iloc[-1]
    ema_slow = ema(close, EMA_SLOW).iloc[-1]
    rsi_value = rsi(close, RSI_PERIOD).iloc[-1]
    macd_line, signal_line, hist = macd(close, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    macd_last = macd_line.iloc[-1]
    macd_signal_last = signal_line.iloc[-1]
    hist_last = hist.iloc[-1]
    upper, mid, lower = bollinger_bands(close, BOLLINGER_PERIOD, BOLLINGER_STD)
    atr_value = atr(high, low, close, ATR_PERIOD).iloc[-1]
    support, resistance = support_resistance(high, low, SUPPORT_RESISTANCE_LOOKBACK)

    current_price = float(close.iloc[-1])
    prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price
    support_level = float(support.iloc[-1])
    resistance_level = float(resistance.iloc[-1])
    lower_band = float(lower.iloc[-1])
    upper_band = float(upper.iloc[-1])

    bullish_score = 0
    bearish_score = 0
    reasons = []

    if ema_fast > ema_slow:
        bullish_score += 2
        reasons.append("EMA trend bullish")
    else:
        bearish_score += 2
        reasons.append("EMA trend bearish")

    if macd_last > macd_signal_last:
        bullish_score += 2
        reasons.append("MACD above signal")
    else:
        bearish_score += 2
        reasons.append("MACD below signal")

    if hist_last > 0:
        bullish_score += 1
        reasons.append("MACD histogram positive")
    else:
        bearish_score += 1
        reasons.append("MACD histogram negative")

    if rsi_value < 30:
        bullish_score += 2
        reasons.append("RSI oversold")
    elif rsi_value > 70:
        bearish_score += 2
        reasons.append("RSI overbought")
    elif 50 <= rsi_value <= 70:
        bullish_score += 1
        reasons.append("RSI favorable")
    else:
        bearish_score += 1
        reasons.append("RSI weak")

    if current_price > support_level:
        bullish_score += 1
        reasons.append("Price above support")
    if current_price < resistance_level:
        bearish_score += 1
        reasons.append("Price below resistance")

    if current_price > lower_band:
        bullish_score += 1
        reasons.append("Price above lower Bollinger band")
    if current_price < upper_band:
        bearish_score += 1
        reasons.append("Price below upper Bollinger band")

    if current_price > prev_price:
        bullish_score += 1
    else:
        bearish_score += 1

    if bullish_score >= bearish_score + 3:
        action = "BUY"
        confidence = latest_signal_strength(bullish_score)
        entry_price = current_price
        stop_loss = current_price * (1 - (STOP_LOSS_PERCENT / 100.0))
        take_profit = current_price * (1 + (TAKE_PROFIT_PERCENT / 100.0))
    elif bearish_score >= bullish_score + 3:
        action = "SELL"
        confidence = latest_signal_strength(bearish_score)
        entry_price = current_price
        stop_loss = current_price * (1 + (STOP_LOSS_PERCENT / 100.0))
        take_profit = current_price * (1 - (TAKE_PROFIT_PERCENT / 100.0))
    else:
        action = "HOLD"
        confidence = 0.0
        entry_price = current_price
        stop_loss = current_price
        take_profit = current_price

    return Signal(
        action=action,
        confidence=confidence,
        reasons=reasons[:6],
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )
