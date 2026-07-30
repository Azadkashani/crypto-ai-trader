"""
Crypto AI Bot v5.2
Trend Engine (Enhanced Strength)
"""

import numpy as np

class TrendEngine:

    @staticmethod
    def detect(df):
        last = df.iloc[-1]
        ema20 = last["EMA20"]
        ema50 = last["EMA50"]
        ema200 = last["EMA200"]
        adx = last["ADX"]

        if adx < 20:
            return "Sideways"
        if ema20 > ema50 > ema200:
            return "Bullish"
        elif ema20 < ema50 < ema200:
            return "Bearish"
        return "Sideways"

    @staticmethod
    def strength(df):
        last = df.iloc[-1]
        # 1. ADX
        adx = last["ADX"]
        # 2. EMA Slope (EMA20 vs EMA50 spread percentage)
        ema_spread = abs(last["EMA20"] - last["EMA50"]) / last["EMA50"] * 100
        # 3. ATR Expansion (current ATR vs average of last 20)
        atr_now = last["ATR"]
        avg_atr = df["ATR"].tail(20).mean()
        atr_expansion = (atr_now / avg_atr - 1) * 100 if avg_atr > 0 else 0
        # 4. Momentum (RSI deviation from 50, MACD histogram positivity)
        rsi = last["RSI"]
        macd_hist = last["MACD_HIST"]
        momentum_score = 0
        if rsi > 55:
            momentum_score += 1
        elif rsi < 45:
            momentum_score -= 1
        if macd_hist > 0:
            momentum_score += 1
        elif macd_hist < 0:
            momentum_score -= 1

        # تصمیم‌گیری بر اساس ترکیب
        strength_points = 0
        if adx >= 40:
            strength_points += 3
        elif adx >= 25:
            strength_points += 2
        elif adx >= 20:
            strength_points += 1

        if ema_spread > 1.5:
            strength_points += 2
        elif ema_spread > 0.8:
            strength_points += 1

        if atr_expansion > 15:
            strength_points += 2
        elif atr_expansion > 5:
            strength_points += 1

        strength_points += momentum_score

        if strength_points >= 6:
            return "Very Strong"
        elif strength_points >= 4:
            return "Strong"
        elif strength_points >= 2:
            return "Medium"
        else:
            return "Weak"

    @staticmethod
    def confidence(df):
        last = df.iloc[-1]
        score = 0
        if last["EMA20"] > last["EMA50"]:
            score += 20
        if last["EMA50"] > last["EMA200"]:
            score += 20
        if last["ADX"] >= 25:
            score += 20
        elif last["ADX"] >= 20:
            score += 10
        if 45 <= last["RSI"] <= 70:
            score += 15
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 15
        volume_mean = df["volume"].tail(20).mean()
        if last["volume"] > volume_mean:
            score += 10
        return min(score, 100)

    @staticmethod
    def alignment(trends):
        bullish = trends.count("Bullish")
        bearish = trends.count("Bearish")
        if bullish == len(trends) or bearish == len(trends):
            return 100
        if bullish == 2 or bearish == 2:
            return 66
        if bullish == 1 or bearish == 1:
            return 33
        return 0
