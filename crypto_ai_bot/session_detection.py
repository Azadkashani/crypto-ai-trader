"""
Crypto AI Bot v1.1
Session Detection – fixed logic, no dead code
"""

from datetime import datetime

class SessionDetection:
    @staticmethod
    def detect():
        now = datetime.utcnow()
        hour = now.hour

        # الویت با باریک‌ترین بازه (Overlap)
        if 12 <= hour < 16:
            return {"session": "London+NY Overlap", "overlap": True}
        # London بدون overlap
        elif 7 <= hour < 12:
            return {"session": "London", "overlap": False}
        # New York بعد از overlap
        elif 16 <= hour < 21:
            return {"session": "New York", "overlap": False}
        # Asia (Tokyo) 0-7 UTC
        elif 0 <= hour < 7:
            return {"session": "Asia", "overlap": False}
        # بقیه ساعات (21-24) دورهٔ آرام
        else:
            return {"session": "Quiet Period", "overlap": False}
