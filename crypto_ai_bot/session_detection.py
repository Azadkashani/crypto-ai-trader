"""
Session Detection based on UTC time
"""

from datetime import datetime

class SessionDetection:
    @staticmethod
    def detect():
        now = datetime.utcnow()
        hour = now.hour
        if 7 <= hour < 16:
            return {"session": "London", "overlap": False}
        elif 12 <= hour < 14:
            return {"session": "London+NY Overlap", "overlap": True}
        elif 1 <= hour < 10:
            return {"session": "Asia", "overlap": False}
        elif 13 <= hour < 21:
            return {"session": "New York", "overlap": False}
        else:
            return {"session": "Quiet Period", "overlap": False}
