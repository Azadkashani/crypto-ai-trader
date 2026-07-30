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

TIMEFRAME = "1h"                # تایم‌فریم اصلی اسکنر
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
