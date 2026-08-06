"""
Crypto AI Bot v1.2
Configuration File (Custom 89 Futures Symbols)
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
USE_ALL_MARKETS = False          # استفاده از لیست دستی
SYMBOLS = [
    "ETH/USDT:USDT",
    "BTC/USDT:USDT",
    "SOL/USDT:USDT",
    "XAU/USDT:USDT",
    "CL/USDT:USDT",
    "HOME/USDT:USDT",
    "XAG/USDT:USDT",
    "XRP/USDT:USDT",
    "ADA/USDT:USDT",
    "BLESS/USDT:USDT",
    "HYPE/USDT:USDT",
    "AKE/USDT:USDT",
    "SKYAI/USDT:USDT",
    "RATS/USDT:USDT",
    "BEAT/USDT:USDT",
    "DOGE/USDT:USDT",
    "BANK/USDT:USDT",
    "ZEC/USDT:USDT",
    "BNB/USDT:USDT",
    "UNI/USDT:USDT",
    "UAI/USDT:USDT",
    "PEPE/USDT:USDT",
    "WLD/USDT:USDT",
    "BZ/USDT:USDT",
    "XAUT/USDT:USDT",
    "UB/USDT:USDT",
    "AVAX/USDT:USDT",
    "GIGGLE/USDT:USDT",
    "BTW/USDT:USDT",
    "BICO/USDT:USDT",
    "CYS/USDT:USDT",
    "GRAM/USDT:USDT",
    "PUMP/USDT:USDT",
    "SUI/USDT:USDT",
    "PAXG/USDT:USDT",
    "ENA/USDT:USDT",
    "KAITO/USDT:USDT",
    "LINK/USDT:USDT",
    "BCH/USDT:USDT",
    "DEXE/USDT:USDT",
    "COTI/USDT:USDT",
    "AAVE/USDT:USDT",
    "TAO/USDT:USDT",
    "NEAR/USDT:USDT",
    "FARTCOIN/USDT:USDT",
    "SHIB/USDT:USDT",
    "DOT/USDT:USDT",
    "EPIC/USDT:USDT",
    "TUT/USDT:USDT",
    "TRUMP/USDT:USDT",
    "HFT/USDT:USDT",
    "LTC/USDT:USDT",
    "LAB/USDT:USDT",
    "WIF/USDT:USDT",
    "KOMA/USDT:USDT",
    "WLFI/USDT:USDT",
    "VANRY/USDT:USDT",
    "XLM/USDT:USDT",
    "LIT/USDT:USDT",
    "US/USDT:USDT",
    "FIL/USDT:USDT",
    "APT/USDT:USDT",
    "ARB/USDT:USDT",
    "ORDI/USDT:USDT",
    "INJ/USDT:USDT",
    "PENGU/USDT:USDT",
    "FET/USDT:USDT",
    "ESPORTS/USDT:USDT",
    "TRX/USDT:USDT",
    "ALLO/USDT:USDT",
    "TIA/USDT:USDT",
    "VELVET/USDT:USDT",
    "LDO/USDT:USDT",
    "IDOL/USDT:USDT",
    "ERA/USDT:USDT",
    "ZAMA/USDT:USDT",
    "ETHFI/USDT:USDT",
    "ICP/USDT:USDT",
    "EUL/USDT:USDT",
    "CFX/USDT:USDT",
    "PTB/USDT:USDT",
    "PIEVERSE/USDT:USDT",
    "PIPPIN/USDT:USDT",
    "ETC/USDT:USDT",
    "CAP/USDT:USDT",
    "RIF/USDT:USDT",
    "VIRTUAL/USDT:USDT",
    "LA/USDT:USDT",
    "VVV/USDT:USDT",
    "BOME/USDT:USDT",
    "XPT/USDT:USDT",
    "SLX/USDT:USDT",
    "ESP/USDT:USDT",
    "PI/USDT:USDT",
    "PEOPLE/USDT:USDT",
    "GALA/USDT:USDT",
    "AEON/USDT:USDT",
    "MMT/USDT:USDT"
]
MAX_SYMBOLS = 100
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
# Account Settings
# ==========================
ACCOUNT_BALANCE = 10000   # سرمایهٔ فرضی (USDT)

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
