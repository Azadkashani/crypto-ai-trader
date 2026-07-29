"""
Volume Profile (ساده شده)
"""

import pandas as pd

class VolumeProfile:
    @staticmethod
    def detect(df, window=20):
        if len(df) < window:
            return {"hvn": None, "lvn": None, "poc": None, "distance_to_poc": None}
        recent = df.tail(window)
        price_range = recent["high"].max() - recent["low"].min()
        if price_range == 0:
            return {"hvn": None, "lvn": None, "poc": recent["close"].iloc[-1], "distance_to_poc": 0}
        bins = 10
        price_step = price_range / bins
        volume_profile = {}
        for i in range(bins):
            lower = recent["low"].min() + i * price_step
            upper = lower + price_step
            mask = (recent["close"] >= lower) & (recent["close"] < upper)
            vol_sum = recent.loc[mask, "volume"].sum()
            volume_profile[(lower, upper)] = vol_sum
        poc_bin = max(volume_profile, key=volume_profile.get)
        poc_price = (poc_bin[0] + poc_bin[1]) / 2
        max_vol = volume_profile[poc_bin]
        hvn = [poc_bin]
        lvn = []
        for bin, vol in volume_profile.items():
            if vol > 0.7 * max_vol and bin != poc_bin:
                hvn.append(bin)
            elif vol < 0.3 * max_vol and vol > 0:
                lvn.append(bin)
        current_price = df["close"].iloc[-1]
        distance_to_poc = abs(current_price - poc_price) / current_price if current_price else 0
        return {
            "hvn": [(l, u) for l, u in hvn],
            "lvn": [(l, u) for l, u in lvn],
            "poc": round(poc_price, 4),
            "distance_to_poc": round(distance_to_poc * 100, 2)
        }
