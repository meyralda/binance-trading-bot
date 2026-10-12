import os
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


# ===== BINANCE API CONFIGURATION =====
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
USE_TESTNET = env_bool("BINANCE_USE_TESTNET", True)
USE_FUTURES = env_bool("BINANCE_USE_FUTURES", True)

# ===== TRADING MODE CONFIGURATION =====
ENABLE_LIVE_TRADING = env_bool("ENABLE_LIVE_TRADING", False)
ENABLE_PAPER_TRADING = env_bool("ENABLE_PAPER_TRADING", True)
TRADING_MODE = os.getenv("TRADING_MODE", "PAPER")  # PAPER, LIVE, BACKTEST

# ===== SYMBOL & TIMEFRAME =====
SYMBOL = os.getenv("BINANCE_SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("BINANCE_INTERVAL", "15m")
CANDLE_LIMIT = int(os.getenv("BINANCE_CANDLE_LIMIT", "200"))

# ===== ACCOUNT & BALANCE =====
MIN_BALANCE_USDT = float(os.getenv("MIN_BALANCE_USDT", "20"))
INITIAL_BALANCE_USDT = float(os.getenv("INITIAL_BALANCE_USDT", "1000"))
POSITION_SIZE_PERCENT = float(os.getenv("POSITION_SIZE_PERCENT", "10"))
RISK_PER_TRADE_PERCENT = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.0"))

# ===== POSITION MANAGEMENT =====
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "3"))
ALLOW_LONG_POSITIONS = env_bool("ALLOW_LONG_POSITIONS", True)
ALLOW_SHORT_POSITIONS = env_bool("ALLOW_SHORT_POSITIONS", True)
USE_LEVERAGE = env_bool("USE_LEVERAGE", False)
LEVERAGE_MULTIPLIER = int(os.getenv("LEVERAGE_MULTIPLIER", "2"))

# ===== STOP LOSS & TAKE PROFIT =====
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "1.5"))
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "3.0"))
TRAILING_STOP_PERCENT = float(os.getenv("TRAILING_STOP_PERCENT", "0.5"))
USE_TRAILING_STOP = env_bool("USE_TRAILING_STOP", False)
BREAK_EVEN_TRIGGER = float(os.getenv("BREAK_EVEN_TRIGGER", "1.5"))

# ===== TREND INDICATORS CONFIGURATION =====
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
EMA_TREND = int(os.getenv("EMA_TREND", "50"))
SMA_LONG = int(os.getenv("SMA_LONG", "200"))

# ===== MOMENTUM INDICATORS CONFIGURATION =====
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", "30"))
RSI_BULLISH = int(os.getenv("RSI_BULLISH", "50"))
RSI_BEARISH = int(os.getenv("RSI_BEARISH", "50"))

# ===== MACD CONFIGURATION =====
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))

# ===== BOLLINGER BANDS CONFIGURATION =====
BOLLINGER_PERIOD = int(os.getenv("BOLLINGER_PERIOD", "20"))
BOLLINGER_STD = float(os.getenv("BOLLINGER_STD", "2.0"))

# ===== STOCHASTIC CONFIGURATION =====
STOCHASTIC_PERIOD = int(os.getenv("STOCHASTIC_PERIOD", "14"))
STOCHASTIC_SMOOTH_K = int(os.getenv("STOCHASTIC_SMOOTH_K", "3"))
STOCHASTIC_SMOOTH_D = int(os.getenv("STOCHASTIC_SMOOTH_D", "3"))
STOCHASTIC_OVERBOUGHT = int(os.getenv("STOCHASTIC_OVERBOUGHT", "80"))
STOCHASTIC_OVERSOLD = int(os.getenv("STOCHASTIC_OVERSOLD", "20"))

# ===== ATR & VOLATILITY CONFIGURATION =====
ATR_PERIOD = int(os.getenv("ATR_PERIOD", "14"))
ATR_MULTIPLIER = float(os.getenv("ATR_MULTIPLIER", "2.0"))

# ===== SUPPORT & RESISTANCE =====
SUPPORT_RESISTANCE_LOOKBACK = int(os.getenv("SUPPORT_RESISTANCE_LOOKBACK", "20"))
PIVOT_PERIOD = int(os.getenv("PIVOT_PERIOD", "14"))

# ===== VOLUME INDICATORS =====
USE_VOLUME_FILTER = env_bool("USE_VOLUME_FILTER", True)
MIN_VOLUME_MULTIPLIER = float(os.getenv("MIN_VOLUME_MULTIPLIER", "1.0"))
OBV_PERIOD = int(os.getenv("OBV_PERIOD", "14"))

# ===== ADX & TREND STRENGTH =====
ADX_PERIOD = int(os.getenv("ADX_PERIOD", "14"))
ADX_THRESHOLD = int(os.getenv("ADX_THRESHOLD", "25"))

# ===== CCI CONFIGURATION =====
CCI_PERIOD = int(os.getenv("CCI_PERIOD", "20"))
CCI_OVERBOUGHT = int(os.getenv("CCI_OVERBOUGHT", "100"))
CCI_OVERSOLD = int(os.getenv("CCI_OVERSOLD", "-100"))

# ===== DIVERGENCE DETECTION =====
USE_DIVERGENCE = env_bool("USE_DIVERGENCE", False)
DIVERGENCE_LOOKBACK = int(os.getenv("DIVERGENCE_LOOKBACK", "10"))

# ===== SIGNAL FILTERING & WEIGHTING =====
MIN_SIGNAL_STRENGTH = float(os.getenv("MIN_SIGNAL_STRENGTH", "0.5"))
REQUIRE_VOLUME_CONFIRMATION = env_bool("REQUIRE_VOLUME_CONFIRMATION", True)
USE_MULTI_TIMEFRAME = env_bool("USE_MULTI_TIMEFRAME", False)

# ===== SCORING WEIGHTS =====
WEIGHT_TREND = float(os.getenv("WEIGHT_TREND", "2.0"))
WEIGHT_MOMENTUM = float(os.getenv("WEIGHT_MOMENTUM", "2.0"))
WEIGHT_VOLATILITY = float(os.getenv("WEIGHT_VOLATILITY", "1.0"))
WEIGHT_VOLUME = float(os.getenv("WEIGHT_VOLUME", "1.0"))
WEIGHT_SUPPORT_RESISTANCE = float(os.getenv("WEIGHT_SUPPORT_RESISTANCE", "1.5"))
WEIGHT_ADX = float(os.getenv("WEIGHT_ADX", "1.5"))

# ===== LONG POSITION THRESHOLDS =====
LONG_MIN_SCORE = float(os.getenv("LONG_MIN_SCORE", "6.0"))
LONG_MIN_RSI = int(os.getenv("LONG_MIN_RSI", "40"))
LONG_MAX_RSI = int(os.getenv("LONG_MAX_RSI", "80"))
LONG_MIN_ADX = int(os.getenv("LONG_MIN_ADX", "20"))

# ===== SHORT POSITION THRESHOLDS =====
SHORT_MIN_SCORE = float(os.getenv("SHORT_MIN_SCORE", "-6.0"))
SHORT_MAX_RSI = int(os.getenv("SHORT_MAX_RSI", "60"))
SHORT_MIN_RSI = int(os.getenv("SHORT_MIN_RSI", "20"))
SHORT_MIN_ADX = int(os.getenv("SHORT_MIN_ADX", "20"))

# ===== COOLDOWN & TRADE TIMING =====
TRADE_COOLDOWN_MINUTES = int(os.getenv("TRADE_COOLDOWN_MINUTES", "5"))
MIN_TIME_BETWEEN_TRADES = int(os.getenv("MIN_TIME_BETWEEN_TRADES", "60"))

# ===== TRADE QUANTITY =====
DEFAULT_TRADE_QUANTITY = float(os.getenv("DEFAULT_TRADE_QUANTITY", "0.0"))
MIN_TRADE_AMOUNT_USDT = float(os.getenv("MIN_TRADE_AMOUNT_USDT", "10"))

# ===== LOGGING & DEBUG =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_SIGNALS = env_bool("LOG_SIGNALS", True)
LOG_INDICATORS = env_bool("LOG_INDICATORS", False)
SAVE_SIGNALS_TO_FILE = env_bool("SAVE_SIGNALS_TO_FILE", False)

# ===== NOTIFICATIONS =====
USE_TELEGRAM = env_bool("USE_TELEGRAM", False)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ===== DATABASE & HISTORY =====
SAVE_TRADE_HISTORY = env_bool("SAVE_TRADE_HISTORY", True)
DATABASE_FILE = os.getenv("DATABASE_FILE", "trade_history.db")

# ===== BACKTEST CONFIGURATION =====
BACKTEST_START_DATE = os.getenv("BACKTEST_START_DATE", "2023-01-01")
BACKTEST_END_DATE = os.getenv("BACKTEST_END_DATE", "2024-01-01")
BACKTEST_COMMISSION = float(os.getenv("BACKTEST_COMMISSION", "0.001"))

# ===== ADVANCED FEATURES =====
USE_MACHINE_LEARNING = env_bool("USE_MACHINE_LEARNING", False)
USE_SENTIMENT_ANALYSIS = env_bool("USE_SENTIMENT_ANALYSIS", False)
ENABLE_AUTO_REBALANCE = env_bool("ENABLE_AUTO_REBALANCE", False)


def get_base_url() -> str:
    if USE_TESTNET:
        if USE_FUTURES:
            return "https://testnet.binancefuture.com"
        return "https://testnet.binance.vision"
    if USE_FUTURES:
        return "https://fapi.binance.com"
    return BASE_URL


def print_config():
    """Print all active configuration for debugging"""
    print("\n" + "=" * 50)
    print("ACTIVE TRADING BOT CONFIGURATION")
    print("=" * 50)
    print(f"Trading Mode: {TRADING_MODE}")
    print(f"Symbol: {SYMBOL} | Interval: {INTERVAL}")
    print(f"Use Testnet: {USE_TESTNET} | Use Futures: {USE_FUTURES}")
    print(f"Live Trading: {ENABLE_LIVE_TRADING} | Paper Trading: {ENABLE_PAPER_TRADING}")
    print(f"\nPositions:")
    print(f"  - Allow Long: {ALLOW_LONG_POSITIONS}")
    print(f"  - Allow Short: {ALLOW_SHORT_POSITIONS}")
    print(f"  - Max Open: {MAX_OPEN_POSITIONS}")
    print(f"  - Use Leverage: {USE_LEVERAGE} (x{LEVERAGE_MULTIPLIER})")
    print(f"\nRisk Management:")
    print(f"  - Stop Loss: {STOP_LOSS_PERCENT}%")
    print(f"  - Take Profit: {TAKE_PROFIT_PERCENT}%")
    print(f"  - Trailing Stop: {TRAILING_STOP_PERCENT}%")
    print(f"  - Risk Per Trade: {RISK_PER_TRADE_PERCENT}%")
    print(f"\nIndicators Enabled:")
    print(f"  - EMA (Fast: {EMA_FAST}, Slow: {EMA_SLOW}, Trend: {EMA_TREND})")
    print(f"  - RSI (Period: {RSI_PERIOD}, OB: {RSI_OVERBOUGHT}, OS: {RSI_OVERSOLD})")
    print(f"  - MACD (Fast: {MACD_FAST}, Slow: {MACD_SLOW}, Signal: {MACD_SIGNAL})")
    print(f"  - Bollinger Bands (Period: {BOLLINGER_PERIOD}, Std: {BOLLINGER_STD})")
    print(f"  - Stochastic (Period: {STOCHASTIC_PERIOD})")
    print(f"  - ATR (Period: {ATR_PERIOD})")
    print(f"  - ADX (Period: {ADX_PERIOD})")
    print(f"  - CCI (Period: {CCI_PERIOD})")
    print(f"  - Volume Filter: {USE_VOLUME_FILTER}")
    print(f"\nSignal Thresholds:")
    print(f"  - Long Min Score: {LONG_MIN_SCORE}")
    print(f"  - Short Min Score: {SHORT_MIN_SCORE}")
    print(f"  - Min Signal Strength: {MIN_SIGNAL_STRENGTH}")
    print("=" * 50 + "\n")
