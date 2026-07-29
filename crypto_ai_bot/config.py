"""
Crypto AI Bot v1.0
Configuration File (Futures)
"""

# ==========================
# Exchange Settings
# ==========================
EXCHANGE_NAME = "gate"
API_KEY = ""
API_SECRET = ""
TESTNET = True

# ==========================
# Trading Settings
# ==========================
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "XRP/USDT",
    "SOL/USDT",
    "DOGE/USDT"
]
USE_ALL_MARKETS = True
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
LEVERAGE = 5
MAX_OPEN_TRADES = 1

# ==========================
# Advanced Analytics Flags
# (True = فعال, False = غیرفعال)
# ==========================
ENABLE_LIQUIDITY_SWEEP = False
ENABLE_FVG = False
ENABLE_ORDER_BLOCK = False
ENABLE_PREMIUM_DISCOUNT = False
ENABLE_VOLUME_PROFILE = False
ENABLE_VWAP = False
ENABLE_OPEN_INTEREST = False
ENABLE_FUNDING_RATE = False
ENABLE_ATR_VOLATILITY = False
ENABLE_EMA_SLOPE = False
ENABLE_RSI_DIVERGENCE = False
ENABLE_MACD_DIVERGENCE = False
ENABLE_CANDLESTICK_PATTERNS = False
ENABLE_SR_STRENGTH = False
ENABLE_BREAKOUT_QUALITY = False
ENABLE_TRENDLINE_BREAK = False
ENABLE_FIBONACCI = False
ENABLE_SESSION_DETECTION = False
ENABLE_MARKET_REGIME = False
ENABLE_CORRELATION_FILTER = False
