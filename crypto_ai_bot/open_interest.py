"""
Crypto AI Bot v1.1
Open Interest Analysis – dynamic price change
"""

import pandas as pd

class OpenInterest:
    @staticmethod
    def detect(symbol, exchange):
        try:
            # دریافت OI ۱ ساعته (دو مقدار آخر)
            oi_data = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
            if len(oi_data) < 2:
                return {"oi_change": 0, "state": "unknown"}

            prev_oi = float(oi_data[-2]["openInterestAmount"])
            curr_oi = float(oi_data[-1]["openInterestAmount"])
            oi_change = ((curr_oi - prev_oi) / prev_oi) * 100 if prev_oi != 0 else 0

            # دریافت دو کندل آخر ۱ ساعته برای محاسبه تغییر قیمت
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=2)
            if len(ohlcv) >= 2:
                prev_close = float(ohlcv[-2][4])
                curr_close = float(ohlcv[-1][4])
                price_change = ((curr_close - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            else:
                price_change = 0

            # طبقه‌بندی وضعیت OI
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
