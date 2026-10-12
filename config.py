import os
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
USE_TESTNET = env_bool("BINANCE_USE_TESTNET", False)
USE_FUTURES = env_bool("BINANCE_USE_FUTURES", False)

ENABLE_LIVE_TRADING = env_bool("ENABLE_LIVE_TRADING", False)
ENABLE_PAPER_TRADING = env_bool("ENABLE_PAPER_TRADING", True)

SYMBOL = os.getenv("BINANCE_SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("BINANCE_INTERVAL", "15m")
CANDLE_LIMIT = int(os.getenv("BINANCE_CANDLE_LIMIT", "200"))

MIN_BALANCE_USDT = float(os.getenv("MIN_BALANCE_USDT", "20"))
INITIAL_BALANCE_USDT = float(os.getenv("INITIAL_BALANCE_USDT", "1000"))
POSITION_SIZE_PERCENT = float(os.getenv("POSITION_SIZE_PERCENT", "10"))
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "1.5"))
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "3.0"))
RISK_PER_TRADE_PERCENT = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.0"))

EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))
BOLLINGER_PERIOD = int(os.getenv("BOLLINGER_PERIOD", "20"))
BOLLINGER_STD = float(os.getenv("BOLLINGER_STD", "2"))
ATR_PERIOD = int(os.getenv("ATR_PERIOD", "14"))
SUPPORT_RESISTANCE_LOOKBACK = int(os.getenv("SUPPORT_RESISTANCE_LOOKBACK", "20"))

DEFAULT_TRADE_QUANTITY = float(os.getenv("DEFAULT_TRADE_QUANTITY", "0.0"))
MIN_TRADE_AMOUNT_USDT = float(os.getenv("MIN_TRADE_AMOUNT_USDT", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_base_url() -> str:
    if USE_TESTNET:
        return "https://testnet.binance.vision"
    return BASE_URL
