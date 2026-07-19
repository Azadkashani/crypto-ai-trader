# ==========================================================
# Crypto AI Bot v4
# Author : Masoud Kashani + ChatGPT
# Version: 4.0
# ==========================================================

import ccxt
import pandas as pd
import ta

# ==========================================================
# SETTINGS
# ==========================================================

TIMEFRAME = "1h"
LIMIT = 500

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT"
]

exchange = ccxt.gate()

# ==========================================================
# DOWNLOAD MARKET DATA
# ==========================================================

def get_market_data(symbol):

    candles = exchange.fetch_ohlcv(
        symbol,
        timeframe=TIMEFRAME,
        limit=LIMIT
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["time"] = pd.to_datetime(
        df["time"],
        unit="ms"
    )

    return df

# ==========================================================
# INDICATORS
# ==========================================================

def calculate_indicators(df):

    df["EMA20"] = ta.trend.ema_indicator(
        df["close"],
        window=20
    )

    df["EMA50"] = ta.trend.ema_indicator(
        df["close"],
        window=50
    )

    df["EMA200"] = ta.trend.ema_indicator(
        df["close"],
        window=200
    )

    df["RSI"] = ta.momentum.rsi(
        df["close"],
        window=14
    )

    df["MACD"] = ta.trend.macd(df["close"])

    df["MACD_SIGNAL"] = ta.trend.macd_signal(
        df["close"]
    )

    df["ATR"] = ta.volatility.average_true_range(
        df["high"],
        df["low"],
        df["close"]
    )

    return df

# ==========================================================
# SUPPORT / RESISTANCE
# ==========================================================

def calculate_levels(df):

    support = df["low"].tail(50).min()

    resistance = df["high"].tail(50).max()

    return support, resistance
