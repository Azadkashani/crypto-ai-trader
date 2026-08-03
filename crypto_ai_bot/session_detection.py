"""
Session Detection based on UTC time
"""

from datetime import datetime

class SessionDetection:
    @staticmethod
    def detect():
        # ترتیب قبلی باعث می‌شد "London+NY Overlap" هیچ‌وقت تشخیص داده نشود
        # (چون بازه‌ی London زودتر و با محدوده‌ی بزرگ‌تر چک می‌شد) و بخشی از
        # ساعات Asia/New York هم به‌اشتباه به‌عنوان London شناسایی می‌شدند.
        # این نسخه بازه‌ها را از خاص‌ترین به عمومی‌ترین و بدون تداخل چک می‌کند.
        now = datetime.utcnow()
        hour = now.hour
        if 12 <= hour < 16:
            return {"session": "London+NY Overlap", "overlap": True}
        elif 7 <= hour < 16:
            return {"session": "London", "overlap": False}
        elif 16 <= hour < 21:
            return {"session": "New York", "overlap": False}
        elif 0 <= hour < 8:
            return {"session": "Asia", "overlap": False}
        else:
            return {"session": "Quiet Period", "overlap": False}
