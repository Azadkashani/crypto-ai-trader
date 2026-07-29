"""
Candlestick Pattern Detection (Manual – بدون ta.candlestick)
"""

import pandas as pd

class CandlestickPatterns:
    @staticmethod
    def detect(df):
        if len(df) < 3:
            return {
                "engulfing_bullish": False,
                "engulfing_bearish": False,
                "hammer": False,
                "shooting_star": False,
                "morning_star": False,
                "evening_star": False,
                "pinbar": False
            }

        # کندل‌های آخر
        c1 = df.iloc[-3]  # دو کندل قبل (برای ستاره‌ها)
        c2 = df.iloc[-2]  # کندل قبلی
        c3 = df.iloc[-1]  # کندل فعلی

        o1, h1, l1, cl1 = c1["open"], c1["high"], c1["low"], c1["close"]
        o2, h2, l2, cl2 = c2["open"], c2["high"], c2["low"], c2["close"]
        o3, h3, l3, cl3 = c3["open"], c3["high"], c3["low"], c3["close"]

        body1 = abs(cl1 - o1)
        body2 = abs(cl2 - o2)
        body3 = abs(cl3 - o3)
        range1 = h1 - l1
        range2 = h2 - l2
        range3 = h3 - l3

        patterns = {}

        # --- Bullish Engulfing ---
        patterns["engulfing_bullish"] = (
            cl2 < o2 and                        # کندل قبل نزولی
            cl3 > o3 and                        # کندل فعلی صعودی
            o3 <= cl2 and cl3 >= o2 and         # بدنه کندل فعلی بدنه کندل قبل را می‌پوشاند
            body3 > body2
        )

        # --- Bearish Engulfing ---
        patterns["engulfing_bearish"] = (
            cl2 > o2 and
            cl3 < o3 and
            o3 >= cl2 and cl3 <= o2 and
            body3 > body2
        )

        # --- Hammer ---
        patterns["hammer"] = (
            body3 > 0 and
            (l3 - min(o3, cl3)) > 2 * body3 and   # سایه پایین بلند
            (max(o3, cl3) - l3) > 0 and
            (h3 - max(o3, cl3)) < 0.3 * body3      # سایه بالا کوچک
        )

        # --- Shooting Star ---
        patterns["shooting_star"] = (
            body3 > 0 and
            (h3 - max(o3, cl3)) > 2 * body3 and
            (min(o3, cl3) - l3) < 0.3 * body3
        )

        # --- Morning Star (3 کندل) ---
        patterns["morning_star"] = (
            cl1 < o1 and                         # کندل اول نزولی بزرگ
            body1 > range1 * 0.6 and
            body2 < range2 * 0.3 and             # کندل دوم کوچک (دوجی/اسپینینگ)
            cl3 > o3 and                         # کندل سوم صعودی
            cl3 > (o1 + cl1) / 2                 # بسته شدن بالای نیمه کندل اول
        )

        # --- Evening Star (3 کندل) ---
        patterns["evening_star"] = (
            cl1 > o1 and
            body1 > range1 * 0.6 and
            body2 < range2 * 0.3 and
            cl3 < o3 and
            cl3 < (o1 + cl1) / 2
        )

        # --- Pinbar (ترکیب Hammer و Shooting Star) ---
        patterns["pinbar"] = patterns["hammer"] or patterns["shooting_star"]

        return patterns
