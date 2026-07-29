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
USE_ALL_MARKETS = True          # اگر True باشد، از صرافی لیست نمادها دریافت می‌شود
MAX_SYMBOLS = 50                # حداکثر تعداد نماد برای اسکن (وقتی USE_ALL_MARKETS فعال است)
TOP_RESULTS = 5                 # تعداد نتایج نهایی نمایش داده‌شده

TIMEFRAME = "1h"                # تایم‌فریم اصلی اسکنر
LIMIT = 200                     # تعداد کندل‌های دریافت‌شده

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
RISK_PER_TRADE = 0.01           # 1% ریسک در هر معامله
MIN_RISK_REWARD = 2.0
LEVERAGE = 5
MAX_OPEN_TRADES = 1
