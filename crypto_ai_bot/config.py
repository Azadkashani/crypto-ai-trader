"""
Crypto AI Bot v1.0
Configuration File (Signal-Only – Gate.io Futures)
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
SYMBOLS = []
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
LEVERAGE = 50          # حداکثر اهرم مجاز (پویا)
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

HIGH_IMPACT_WINDOW_MINUTES = 30

ECONOMIC_CALENDAR_API_URL = "https://example.com/calendar"
ECONOMIC_CALENDAR_ENABLED = False
