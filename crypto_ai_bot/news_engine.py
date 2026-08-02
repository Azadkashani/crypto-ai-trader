"""
Crypto AI Bot
News Engine – using feedparser for reliable RSS parsing
"""

import feedparser
from datetime import datetime, timedelta
from config import NEWS_SOURCES, NEWS_MAX_AGE_HOURS

class NewsEngine:
    @staticmethod
    def fetch_news(symbol=None):
        all_news = []
        for source in NEWS_SOURCES:
            try:
                print(f"Fetching {source['name']}...")
                feed = feedparser.parse(source["url"])
                entries = feed.entries
                print(f"  Found {len(entries)} items")
                for entry in entries:
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    # time parsing with feedparser
                    pub_dt = None
                    if "published_parsed" in entry:
                        try:
                            pub_dt = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    if not pub_dt and "updated_parsed" in entry:
                        try:
                            pub_dt = datetime(*entry.updated_parsed[:6])
                        except:
                            pass
                    if pub_dt:
                        if datetime.utcnow() - pub_dt > timedelta(hours=NEWS_MAX_AGE_HOURS):
                            continue
                    all_news.append({
                        "title": title,
                        "link": link,
                        "source": source["name"],
                        "timestamp": entry.get("published", "")
                    })
            except Exception as e:
                print(f"  Error for {source['name']}: {e}")

        print(f"Total news fetched: {len(all_news)}")
        return all_news
