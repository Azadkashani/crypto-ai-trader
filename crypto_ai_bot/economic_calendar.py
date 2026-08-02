"""
Crypto AI Bot v1.1
Economic Calendar – simulated high-impact events
"""

from datetime import datetime, timedelta

class EconomicCalendar:
    @staticmethod
    def fetch_events():
        now = datetime.utcnow()
        return [
            {"title": "FOMC Minutes", "time": (now + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M"),
             "country": "USD", "impact": "high", "actual": None, "forecast": None, "previous": None},
            {"title": "CPI Data", "time": (now + timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M"),
             "country": "USD", "impact": "high", "actual": None, "forecast": None, "previous": None},
        ]
