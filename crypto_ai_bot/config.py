"""
Crypto AI Bot v5
Configuration File
"""

# =====================================================
# Exchange Settings
# =====================================================

EXCHANGE_NAME = "gate"

# =====================================================
# Market Data
# =====================================================

TIMEFRAME = "1h"

LIMIT = 500

# =====================================================
# Manual Symbols
# =====================================================

SYMBOLS = [

    "BTC/USDT",

    "ETH/USDT",

    "SOL/USDT",

    "XRP/USDT",

    "DOGE/USDT",

]

# =====================================================
# Automatic Market Scanner
# =====================================================

USE_ALL_MARKETS = False

QUOTE_CURRENCY = "USDT"

MAX_SYMBOLS = 100

TOP_RESULTS = 10

# =====================================================
# Indicator Settings
# =====================================================

EMA_FAST = 20

EMA_MID = 50

EMA_SLOW = 200

RSI_PERIOD = 14

MACD_FAST = 12

MACD_SLOW = 26

MACD_SIGNAL = 9

ATR_PERIOD = 14

# =====================================================
# Support & Resistance
# =====================================================

SUPPORT_LOOKBACK = 50

RESISTANCE_LOOKBACK = 50

# =====================================================
# Score Settings
# =====================================================

BUY_SCORE = 80

WATCH_SCORE = 60
