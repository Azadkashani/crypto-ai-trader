"""
Open Interest Analysis (نیازمند داده صرافی)
"""

class OpenInterest:
    @staticmethod
    def detect(symbol, exchange, df=None):
        try:
            oi_data = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
            if len(oi_data) < 2:
                return {"oi_change": 0, "state": "unknown"}
            prev_oi = oi_data[-2]["openInterestAmount"]
            curr_oi = oi_data[-1]["openInterestAmount"]
            oi_change = ((curr_oi - prev_oi) / prev_oi) * 100 if prev_oi else 0

            # محاسبه واقعی تغییر قیمت (قبلاً همیشه 0 بود و باعث می‌شد
            # حالت‌های Long Build Up / Short Covering هیچ‌وقت رخ ندهند)
            price_change = 0
            if df is not None and len(df) >= 2:
                prev_close = float(df["close"].iloc[-2])
                curr_close = float(df["close"].iloc[-1])
                if prev_close:
                    price_change = ((curr_close - prev_close) / prev_close) * 100

            if oi_change > 0:
                if price_change > 0:
                    state = "Long Build Up"
                else:
                    state = "Short Build Up"
            elif oi_change < 0:
                if price_change > 0:
                    state = "Short Covering"
                else:
                    state = "Long Unwinding"
            else:
                state = "Stable"
            return {"oi_change": round(oi_change, 2), "state": state}
        except Exception:
            return {"oi_change": 0, "state": "unavailable"}
