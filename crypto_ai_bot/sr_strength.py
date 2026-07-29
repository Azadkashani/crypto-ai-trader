"""
Support / Resistance Strength
"""

class SRStrength:
    @staticmethod
    def detect(df):
        resistance = df["high"].tail(50).max()
        support = df["low"].tail(50).min()
        # استفاده از sum روی boolean Series به‌جای فیلتر مستقیم DataFrame
        touches_res = (abs(df["high"].tail(50) - resistance) / resistance < 0.005).sum()
        touches_sup = (abs(df["low"].tail(50) - support) / support < 0.005).sum()
        return {
            "resistance_level": resistance,
            "support_level": support,
            "resistance_touches": int(touches_res),
            "support_touches": int(touches_sup),
            "valid_resistance": touches_res >= 3,
            "valid_support": touches_sup >= 3
        }
