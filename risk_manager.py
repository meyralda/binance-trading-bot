from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from binance import Client

from config import (
    API_KEY,
    API_SECRET,
    SYMBOL,
    USE_TESTNET,
    BASE_URL,
    ENABLE_LIVE_TRADING,
)


@dataclass
class AccountBalance:
    asset: str
    free: float
    locked: float


class BinanceClient:
    def __init__(self, api_key: str = API_KEY, api_secret: str = API_SECRET):
        self.client = Client(api_key, api_secret, testnet=USE_TESTNET)
        if USE_TESTNET:
            self.client.API_URL = BASE_URL.replace("https://api.binance.com", "https://testnet.binance.vision")

    def get_klines(self, symbol: str = SYMBOL, interval: str = "15m", limit: int = 200):
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_current_price(self, symbol: str = SYMBOL) -> float:
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])

    def get_account_balances(self) -> List[AccountBalance]:
        account = self.client.get_account()
        balances = []
        for asset in account.get("balances", []):
            if float(asset.get("free", 0)) > 0 or float(asset.get("locked", 0)) > 0:
                balances.append(AccountBalance(
                    asset=asset["asset"],
                    free=float(asset.get("free", 0)),
                    locked=float(asset.get("locked", 0)),
                ))
        return balances

    def get_balance(self, asset: str = "USDT") -> float:
        for balance in self.get_account_balances():
            if balance.asset == asset:
                return balance.free + balance.locked
        return 0.0

    def place_market_order(self, symbol: str, side: str, quantity: float):
        if not ENABLE_LIVE_TRADING:
            raise RuntimeError("Live trading is disabled. Set ENABLE_LIVE_TRADING=True to place real orders.")
        if not API_KEY or not API_SECRET:
            raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set before live trading.")
        return self.client.order_market_buy(symbol=symbol, quantity=quantity) if side == "BUY" else self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def get_server_time(self):
        return self.client.get_server_time()


def get_client() -> BinanceClient:
    return BinanceClient()
