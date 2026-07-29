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

    @staticmethod
    def _get_trend(highs, lows):
        """
        استخراج روند از ساختار HH+HL و LH+LL
        نیاز به حداقل دو High و دو Low دارد
        """
        if len(highs) < 2 or len(lows) < 2:
            return "sideways"
        if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
            return "bullish"
        elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
            return "bearish"
        else:
            return "sideways"

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

        for p in points:
            idx = p["index"]
            price = p["price"]
            close = float(df["close"].iloc[idx])   # Close کندل متناظر با Swing

            if p["type"] == "high":
                # روند قبل از این Swing
                trend_before = cls._get_trend(prev_highs, prev_lows)
                last_high = prev_highs[-1] if prev_highs else None

                # تعیین برچسب HH/LH
                if last_high is None:
                    label = None
                else:
                    label = "HH" if price > last_high else "LH"

                # تشخیص BOS/CHoCH در صورت شکست صعودی
                if last_high is not None and price > last_high:
                    if cls._confirm_break(price, last_high, close, "bullish"):
                        if trend_before == "bearish":
                            choch_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bullish"
                            })
                        else:  # bullish یا sideways
                            bos_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bullish"
                            })

                # به‌روزرسانی لیست‌ها
                prev_highs.append(price)
                labeled_highs.append({
                    "index": idx,
                    "price": price,
                    "label": label
                })

            else:  # low
                trend_before = cls._get_trend(prev_highs, prev_lows)
                last_low = prev_lows[-1] if prev_lows else None

                if last_low is None:
                    label = None
                else:
                    label = "HL" if price > last_low else "LL"

                if last_low is not None and price < last_low:
                    if cls._confirm_break(price, last_low, close, "bearish"):
                        if trend_before == "bullish":
                            choch_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bearish"
                            })
                        else:  # bearish یا sideways
                            bos_events.append({
                                "index": idx,
                                "price": price,
                                "type": "bearish"
                            })

                prev_lows.append(price)
                labeled_lows.append({
                    "index": idx,
                    "price": price,
                    "label": label
                })

        # روند نهایی بر اساس کل Swingهای مشاهده‌شده
        final_trend = cls._get_trend(prev_highs, prev_lows)
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
