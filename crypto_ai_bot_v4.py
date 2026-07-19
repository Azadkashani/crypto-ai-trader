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

# ==========================================================
# TREND ENGINE
# ==========================================================

def detect_trend(last):

    if (
        last["EMA20"] >
        last["EMA50"] >
        last["EMA200"]
    ):
        return "Bullish"

    elif (
        last["EMA20"] <
        last["EMA50"] <
        last["EMA200"]
    ):
        return "Bearish"

    return "Sideways"


# ==========================================================
# SCORE ENGINE
# ==========================================================

def calculate_score(df):

    last = df.iloc[-1]

    score = 0

    reasons = []

    # EMA
    if last["EMA20"] > last["EMA50"]:
        score += 25
        reasons.append("EMA20 > EMA50")

    if last["EMA50"] > last["EMA200"]:
        score += 25
        reasons.append("EMA50 > EMA200")

    # RSI
    if 45 <= last["RSI"] <= 70:
        score += 20
        reasons.append("Healthy RSI")

    # MACD
    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 20
        reasons.append("Bullish MACD")

    # Volume
    avg_volume = df["volume"].tail(20).mean()

    if last["volume"] > avg_volume:
        score += 10
        reasons.append("High Volume")

    return score, reasons


# ==========================================================
# ACTION ENGINE
# ==========================================================

def detect_action(score):

    if score >= 80:
        return "BUY"

    elif score >= 60:
        return "WATCH"

    return "NO TRADE"


# ==========================================================
# ANALYZE SYMBOL
# ==========================================================

def analyze_symbol(symbol):

    df = get_market_data(symbol)

    df = calculate_indicators(df)

    support, resistance = calculate_levels(df)

    last = df.iloc[-1]

    trend = detect_trend(last)

    score, reasons = calculate_score(df)

    action = detect_action(score)

    result = {

        "Symbol": symbol,

        "Price": round(last["close"],4),

        "Support": round(support,4),

        "Resistance": round(resistance,4),

        "RSI": round(last["RSI"],2),

        "Score": score,

        "Trend": trend,

        "Action": action,

        "Reasons": ", ".join(reasons)

    }

    return result
