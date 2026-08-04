"""
Crypto AI Bot v1.2
Configuration File (Adaptive Position Sizing, Liquidity Execution, Expected Value)
"""

# ==========================
# Exchange Settings
# ==========================
EXCHANGE_NAME = "gate"
API_KEY = ""
API_SECRET = ""
TESTNET = False

# ==========================
# Trading Settings
# ==========================
USE_ALL_MARKETS = False
SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "XRP/USDT:USDT",
    "SOL/USDT:USDT",
    "DOGE/USDT:USDT",
    "BNB/USDT:USDT",
    "ADA/USDT:USDT",
    "LINK/USDT:USDT",
    "AVAX/USDT:USDT",
    "LTC/USDT:USDT",
    "TRX/USDT:USDT",
    "BCH/USDT:USDT",
    "DOT/USDT:USDT",
    "ETC/USDT:USDT",
    "ATOM/USDT:USDT",
    "FIL/USDT:USDT",
    "NEAR/USDT:USDT",
    "APT/USDT:USDT",
    "ARB/USDT:USDT",
    "OP/USDT:USDT",
    "SUI/USDT:USDT",
    "INJ/USDT:USDT",
    "SEI/USDT:USDT",
    "AAVE/USDT:USDT",
    "UNI/USDT:USDT",
    "CRV/USDT:USDT",
    "ICP/USDT:USDT",
    "ALGO/USDT:USDT",
    "XLM/USDT:USDT",
    "HBAR/USDT:USDT",
    "VET/USDT:USDT",
    "GRT/USDT:USDT",
    "SAND/USDT:USDT",
    "MANA/USDT:USDT",
    "FLOW/USDT:USDT",
    "THETA/USDT:USDT",
    "ROSE/USDT:USDT",
    "ZEC/USDT:USDT",
    "COMP/USDT:USDT",
    "SNX/USDT:USDT",
    "KAVA/USDT:USDT",
    "CHZ/USDT:USDT",
    "APE/USDT:USDT",
    "LDO/USDT:USDT",
    "RUNE/USDT:USDT",
    "EGLD/USDT:USDT",
    "KSM/USDT:USDT",
    "ZRX/USDT:USDT",
    "QTUM/USDT:USDT"
]
MAX_SYMBOLS = 50
TOP_RESULTS = 5

TIMEFRAME = "1h"
LIMIT = 200

# ==========================
# Indicator Parameters
# ==========================
EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200
RSI_PERIOD = 14
ATR_PERIOD = 14

# ==========================
# Scoring Thresholds
# ==========================
BUY_SCORE = 75
WATCH_SCORE = 50

# ==========================
# Risk Management (Futures)
# ==========================
RISK_PER_TRADE = 0.01
MIN_RISK_REWARD = 2.0
LEVERAGE = 50
MAX_OPEN_TRADES = 1

# ==========================
# Trading Execution Settings
# ==========================
TRAILING_STOP_ENABLED = True
TRAILING_STOP_ACTIVATION = 0.5
SCAN_INTERVAL_MINUTES = 5

# ==========================
# Advanced Analytics Flags
# ==========================
ENABLE_LIQUIDITY_SWEEP = True
ENABLE_FVG = True
ENABLE_ORDER_BLOCK = True
ENABLE_PREMIUM_DISCOUNT = True
ENABLE_VOLUME_PROFILE = True
ENABLE_VWAP = True
ENABLE_OPEN_INTEREST = True
ENABLE_FUNDING_RATE = True
ENABLE_ATR_VOLATILITY = True
ENABLE_EMA_SLOPE = True
ENABLE_RSI_DIVERGENCE = True
ENABLE_MACD_DIVERGENCE = True
ENABLE_CANDLESTICK_PATTERNS = True
ENABLE_SR_STRENGTH = True
ENABLE_BREAKOUT_QUALITY = True
ENABLE_TRENDLINE_BREAK = True
ENABLE_FIBONACCI = True
ENABLE_SESSION_DETECTION = True
ENABLE_MARKET_REGIME = True
ENABLE_CORRELATION_FILTER = True

# ==========================
# News & Sentiment Settings
# ==========================
ENABLE_NEWS_ENGINE = True
ENABLE_ECONOMIC_CALENDAR = False
ENABLE_SENTIMENT_ENGINE = True

NEWS_SOURCES = [
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "type": "rss"},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "type": "rss"},
]
NEWS_MAX_AGE_HOURS = 6

ALTERNATIVE_ME_API_URL = "https://api.alternative.me/fng/"
FEAR_GREED_ENABLED = True

NEWS_WEIGHT_IN_SCORE = 0.15
SENTIMENT_WEIGHT_IN_SCORE = 0.10
NEWS_WEIGHT_IN_CONFIDENCE = 0.10
SENTIMENT_WEIGHT_IN_CONFIDENCE = 0.05

HIGH_IMPACT_WINDOW_MINUTES = 60

# ==========================
# Minimum 24h Volume Filter
# ==========================
MIN_24H_VOLUME = 1000000

# ==========================
# Adaptive Position Sizing
# ==========================
ENABLE_ADAPTIVE_POSITION_SIZING = True
MIN_POSITION_RISK = 0.0025   # 0.25%
MAX_POSITION_RISK = 0.01     # 1%

# ==========================
# Liquidity Execution
# ==========================
ENABLE_LIQUIDITY_EXECUTION = True
MIN_EXECUTION_QUALITY = 70

# ==========================
# Expected Value
# ==========================
ENABLE_EXPECTED_VALUE = True
MIN_EXPECTED_VALUE = 0
