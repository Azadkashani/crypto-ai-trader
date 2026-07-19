"""
Crypto AI Bot v4
Configuration File
"""

# -----------------------------
# Exchange
# -----------------------------

EXCHANGE_NAME = "gate"

# -----------------------------
# Timeframe
# -----------------------------

TIMEFRAME = "1h"

# -----------------------------
# Number of Candles
# -----------------------------

LIMIT = 500

# -----------------------------
# Symbols
# -----------------------------

SYMBOLS = [

    "BTC/USDT",

    "ETH/USDT",

    "SOL/USDT",

    "XRP/USDT",

    "DOGE/USDT",

]

# -----------------------------
# Indicator Settings
# -----------------------------

EMA_FAST = 20

EMA_MID = 50

EMA_SLOW = 200

RSI_PERIOD = 14

MACD_FAST = 12

MACD_SLOW = 26

MACD_SIGNAL = 9

ATR_PERIOD = 14

# -----------------------------
# Scanner
# -----------------------------

SUPPORT_LOOKBACK = 50

RESISTANCE_LOOKBACK = 50

# -----------------------------
# Score Settings
# -----------------------------

BUY_SCORE = 80

WATCH_SCORE = 60
# -----------------------------
# Market Scanner
# -----------------------------

QUOTE_CURRENCY = "USDT"

TOP_RESULTS = 10
