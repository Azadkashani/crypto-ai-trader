"""
Crypto AI Bot
News Engine – دریافت اخبار از منابع معتبر
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from config import NEWS_SOURCES, NEWS_MAX_AGE_HOURS

class NewsEngine:
    @staticmethod
    def fetch_news(symbol=None):
        """
        دریافت اخبار از RSS های تعریف‌شده.
        symbol (اختیاری): برای فیلتر کردن اخبار مرتبط.
        بازگشت: لیستی از دیکشنری‌های خبر.
        """
        all_news = []
        for source in NEWS_SOURCES:
            try:
                if source["type"] == "rss":
                    resp = requests.get(source["url"], timeout=10)
                    root = ET.fromstring(resp.content)
                    for item in root.iter("item"):
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        # فیلتر زمانی
                        try:
                            pub_dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                            age = datetime.now(pub_dt.tzinfo) - pub_dt
                            if age > timedelta(hours=NEWS_MAX_AGE_HOURS):
                                continue
                        except:
                            pass
                        all_news.append({
                            "title": title,
                            "link": link,
                            "source": source["name"],
                            "timestamp": pub_date
                        })
                # می‌توان انواع دیگر مانند API را اضافه کرد
            except Exception as e:
                print(f"News fetch error ({source['name']}): {e}")

        return all_news
