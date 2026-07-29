"""
Open Interest Analysis (نیازمند داده صرافی)
"""

class OpenInterest:
    @staticmethod
    def detect(symbol, exchange):
        try:
            oi_data = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
            if len(oi_data) < 2:
                return {"oi_change": 0, "state": "unknown"}
            prev_oi = oi_data[-2]["openInterestAmount"]
            curr_oi = oi_data[-1]["openInterestAmount"]
            oi_change = ((curr_oi - prev_oi) / prev_oi) * 100 if prev_oi else 0
            price_change = 0
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
