"""
Crypto AI Bot
News Engine – دریافت اخبار از RSS با پردازش قوی
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from config import NEWS_SOURCES, NEWS_MAX_AGE_HOURS

class NewsEngine:
    @staticmethod
    def fetch_news(symbol=None):
        all_news = []
        for source in NEWS_SOURCES:
            try:
                print(f"Fetching {source['name']}...")
                resp = requests.get(source["url"], timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                resp.raise_for_status()
                
                # پاک‌سازی محتوای XML برای جلوگیری از خطاهای namespace
                content = resp.text
                root = ET.fromstring(content)
                
                # جستجوی item در کل ساختار (گاهی با namespace همراه است)
                items = root.findall('.//item')
                if not items:
                    items = root.findall('./channel/item')
                
                print(f"  Found {len(items)} items")
                
                for item in items:
                    title_el = item.find('title')
                    link_el = item.find('link')
                    pub_el = item.find('pubDate')
                    
                    title = title_el.text if title_el is not None else ''
                    link = link_el.text if link_el is not None else ''
                    pub_date = pub_el.text if pub_el is not None else ''
                    
                    if not title:
                        continue
                        
                    # بررسی تازگی خبر
                    try:
                        pub_dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                        if datetime.now(pub_dt.tzinfo) - pub_dt > timedelta(hours=NEWS_MAX_AGE_HOURS):
                            continue
                    except:
                        pass  # اگر تاریخ قابل تشخیص نبود، خبر را نگه می‌داریم
                    
                    all_news.append({
                        "title": title.strip(),
                        "link": link,
                        "source": source["name"],
                        "timestamp": pub_date
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"  Request error for {source['name']}: {e}")
            except ET.ParseError as e:
                print(f"  XML parsing error for {source['name']}: {e}")
            except Exception as e:
                print(f"  Unexpected error for {source['name']}: {e}")
                
        print(f"Total news fetched: {len(all_news)}")
        return all_news
