"""
Crypto AI Bot v1.1
Risk Event Detection – high impact news within 60 minutes
"""

from datetime import datetime, timedelta
from config import HIGH_IMPACT_WINDOW_MINUTES

class RiskEvents:
    @staticmethod
    def is_high_impact_near(calendar_events):
        now = datetime.utcnow()
        window = timedelta(minutes=HIGH_IMPACT_WINDOW_MINUTES)
        for event in calendar_events:
            if event.get("impact") == "high":
                event_time = datetime.strptime(event["time"], "%Y-%m-%d %H:%M")
                if abs(now - event_time) < window:
                    return True, event
        return False, None
