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
    def _confirm_break(price, level, close, direction):
        """
        بررسی تأیید شکست با استفاده از کندل Close
        direction: 'bullish' (شکست مقاومت) یا 'bearish' (شکست حمایت)
        """
        if direction == "bullish":
            return price > level and close > level
        elif direction == "bearish":
            return price < level and close < level
        return False

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
        prev_highs = []   # قیمت‌های Swing High به ترتیب ظهور
        prev_lows = []    # قیمت‌های Swing Low به ترتیب ظهور

        labeled_highs = []
        labeled_lows = []
        bos_events = []
        choch_events = []

        # وضعیت فعلی روند فقط با BOS تغییر می‌کند
        direction = "sideways"

        # پرچم برای جلوگیری از CHoCH تکراری تا زمان تغییر روند
        choch_triggered = {"bullish": False, "bearish": False}

        for p in points:
            idx = p["index"]
            price = p["price"]
            close = float(df["close"].iloc[idx])   # Close کندل متناظر با Swing

            if p["type"] == "high":
                last_high = prev_highs[-1] if prev_highs else None

                # تعیین برچسب HH/LH بر اساس مقایسه با High قبلی
                if last_high is None:
                    label = None
                else:
                    label = "HH" if price > last_high else "LH"

                # تشخیص BOS/CHoCH
                if last_high is not None and price > last_high:
                    if cls._confirm_break(price, last_high, close, "bullish"):
                        if direction == "bearish":
                            # در روند نزولی، شکست صعودی = CHoCH (اخطار)
                            if not choch_triggered["bullish"]:
                                choch_events.append({
                                    "index": idx,
                                    "price": price,
                                    "type": "bullish"
                                })
                                choch_triggered["bullish"] = True
                            # direction تغییر نمی‌کند
                        else:
                            # در روند صعودی یا خنثی = BOS (تأیید/شروع روند صعودی)
                            bos_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bullish"
                            })
                            direction = "bullish"
                            # بازنشانی پرچم‌های CHoCH با تغییر روند
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
                    if cls._confirm_break(price, last_low, close, "bearish"):
                        if direction == "bullish":
                            # در روند صعودی، شکست نزولی = CHoCH
                            if not choch_triggered["bearish"]:
                                choch_events.append({
                                    "index": idx,
                                    "price": price,
                                    "type": "bearish"
                                })
                                choch_triggered["bearish"] = True
                        else:
                            # در روند نزولی یا خنثی = BOS
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

        return {
            "swing_highs": labeled_highs,
            "swing_lows": labeled_lows,
            "last_high": last_high_val,
            "last_low": last_low_val,
            "bos": bos_events,
            "choch": choch_events,
            "trend": final_trend
        }
