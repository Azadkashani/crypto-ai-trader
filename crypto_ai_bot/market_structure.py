"""
Crypto AI Bot
Phase 1 - Step 1
Market Structure (Swing Engine)
"""

PIVOT_LENGTH = 5

class MarketStructure:

    @staticmethod
    def _is_pivot_high(df, i, length=PIVOT_LENGTH):
        if i < length or i >= len(df) - length:
            return False
        h = df["high"].iloc[i]
        return all(h > df["high"].iloc[j] for j in range(i - length, i)) and all(
            h >= df["high"].iloc[j] for j in range(i + 1, i + length + 1)
        )

    @staticmethod
    def _is_pivot_low(df, i, length=PIVOT_LENGTH):
        if i < length or i >= len(df) - length:
            return False
        l = df["low"].iloc[i]
        return all(l < df["low"].iloc[j] for j in range(i - length, i)) and all(
            l <= df["low"].iloc[j] for j in range(i + 1, i + length + 1)
        )

    @staticmethod
    def _confirm_break(df, i, level, direction):
        """
        تأیید شکست ساختاری با Close، حجم و ATR
        """
        close = float(df["close"].iloc[i])
        volume = float(df["volume"].iloc[i])
        avg_volume = float(df["AVG_VOLUME"].iloc[i])

        if direction == "bullish":
            if not (close > level):
                return False
        else:
            if not (close < level):
                return False

        if volume < avg_volume:
            return False

        if "ATR" in df.columns:
            atr = float(df["ATR"].iloc[i])
            distance = abs(close - level)
            if distance < 0.2 * atr:
                return False

        return True

    @classmethod
    def analyze(cls, df):
        # استخراج Swing High و Low
        swing_highs_raw = []
        swing_lows_raw = []

        for i in range(len(df)):
            if cls._is_pivot_high(df, i):
                swing_highs_raw.append({
                    "index": i,
                    "price": float(df["high"].iloc[i])
                })
            if cls._is_pivot_low(df, i):
                swing_lows_raw.append({
                    "index": i,
                    "price": float(df["low"].iloc[i])
                })

        # ادغام و مرتب‌سازی نقاط بر اساس زمان
        points = []
        for sh in swing_highs_raw:
            points.append({"index": sh["index"], "price": sh["price"], "type": "high"})
        for sl in swing_lows_raw:
            points.append({"index": sl["index"], "price": sl["price"], "type": "low"})
        points.sort(key=lambda x: x["index"])

        # متغیرهای تحلیل ساختار
        prev_highs = []
        prev_lows = []

        labeled_highs = []
        labeled_lows = []
        bos_events = []
        choch_events = []

        direction = "sideways"
        choch_triggered = {"bullish": False, "bearish": False}

        for p in points:
            idx = p["index"]
            price = p["price"]

            if p["type"] == "high":
                last_high = prev_highs[-1] if prev_highs else None

                if last_high is None:
                    label = None
                else:
                    label = "HH" if price > last_high else "LH"

                if last_high is not None and price > last_high:
                    if cls._confirm_break(df, idx, last_high, "bullish"):
                        if direction == "bearish":
                            if not choch_triggered["bullish"]:
                                choch_events.append({
                                    "index": idx,
                                    "price": price,
                                    "type": "bullish"
                                })
                                choch_triggered["bullish"] = True
                            # جهت تغییر نمی‌کند
                        else:
                            bos_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bullish"
                            })
                            direction = "bullish"
                            choch_triggered = {"bullish": False, "bearish": False}

                prev_highs.append(price)
                labeled_highs.append({
                    "index": idx,
                    "price": price,
                    "label": label
                })

            else:  # low
                last_low = prev_lows[-1] if prev_lows else None

                if last_low is None:
                    label = None
                else:
                    label = "HL" if price > last_low else "LL"

                if last_low is not None and price < last_low:
                    if cls._confirm_break(df, idx, last_low, "bearish"):
                        if direction == "bullish":
                            if not choch_triggered["bearish"]:
                                choch_events.append({
                                    "index": idx,
                                    "price": price,
                                    "type": "bearish"
                                })
                                choch_triggered["bearish"] = True
                        else:
                            bos_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bearish"
                            })
                            direction = "bearish"
                            choch_triggered = {"bullish": False, "bearish": False}

                prev_lows.append(price)
                labeled_lows.append({
                    "index": idx,
                    "price": price,
                    "label": label
                })

        # روند نهایی = آخرین جهت تعیین‌شده توسط BOS
        final_trend = direction

        last_high_val = labeled_highs[-1]["price"] if labeled_highs else None
        last_low_val = labeled_lows[-1]["price"] if labeled_lows else None

        # جمع‌آوری آخرین رویداد ساختاری (برای تشخیص Opposing CHoCH)
        all_events = []
        for ev in bos_events:
            all_events.append({**ev, "event": "bos"})
        for ev in choch_events:
            all_events.append({**ev, "event": "choch"})
        all_events.sort(key=lambda x: x["index"])
        last_event = all_events[-1] if all_events else None

        return {
            "swing_highs": labeled_highs,
            "swing_lows": labeled_lows,
            "last_high": last_high_val,
            "last_low": last_low_val,
            "bos": bos_events,
            "choch": choch_events,
            "trend": final_trend,
            "last_event": last_event
        }
