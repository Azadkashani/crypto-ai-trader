"""
Order Block Detection (SMC Style) - No Warnings
"""

import pandas as pd

class OrderBlock:
    @staticmethod
    def detect(df, market_structure=None):
        if len(df) < 5:
            return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
        bos = market_structure.get("bos", []) if market_structure else []
        if not bos:
            return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
        last_bos = bos[-1]
        bos_idx = last_bos["index"]

        if bos_idx > 0:
            ob_candle = df.iloc[bos_idx - 1]
            # بخش بعد از BOS
            subsequent = df.iloc[bos_idx:].copy()
            
            if last_bos["type"] == "bullish" and ob_candle["close"] < ob_candle["open"]:
                ob_high = ob_candle["high"]
                ob_low = ob_candle["low"]
                # استفاده از .values برای جلوگیری از مشکل index
                touches = int((subsequent["low"].values <= ob_high).sum())
                return {
                    "bullish_ob": {"high": ob_high, "low": ob_low},
                    "bearish_ob": None,
                    "valid": True,
                    "touches": touches
                }
            elif last_bos["type"] == "bearish" and ob_candle["close"] > ob_candle["open"]:
                ob_high = ob_candle["high"]
                ob_low = ob_candle["low"]
                touches = int((subsequent["high"].values >= ob_low).sum())
                return {
                    "bullish_ob": None,
                    "bearish_ob": {"high": ob_high, "low": ob_low},
                    "valid": True,
                    "touches": touches
                }
        return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
