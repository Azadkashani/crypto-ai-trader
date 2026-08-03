"""
Crypto AI Bot v1.1
Advanced Report Engine (Smart Price Display, Volume USDT, Single Target with R:R)
"""

import pandas as pd

def smart_price(price):
    if price is None: return "N/A"
    if abs(price) < 0.01:
        s = f"{price:.8f}"
        return s.rstrip('0').rstrip('.') if '.' in s else s
    return f"{price:.4f}"

class ReportEngine:
    @staticmethod
    def show(results):
        if not results: print("No Data"); return

        table = pd.DataFrame(results)
        table = table.sort_values(by="Trade Readiness", ascending=False)

        print("\n" + "=" * 140)
        print("CRYPTO AI BOT MARKET SCANNER v1.1")
        print("=" * 140)

        columns = [
            "Symbol", "Price", "VolumeUSDT", "Trend", "Strength", "MTF_Signal",
            "Confidence", "RSI", "News Score", "Sentiment Score",
            "Score", "Action", "Entry Quality", "Trade Readiness",
            "Leverage", "InputPct"
        ]
        cols = [c for c in columns if c in table.columns]
        print(table[cols].to_string(index=False))
        print("=" * 140)
        print("\n🏆 Top Opportunities Ranking:\n")

        top_n = min(3, len(results))
        for i in range(top_n):
            item = results[i]
            entry = item.get("Entry", 0)
            sl = item.get("StopLoss", 0)
            tp1 = item.get("TP1", item.get("TakeProfit", 0))

            sl_pct = ((sl - entry) / entry) * 100 if entry else 0
            tp1_pct = ((tp1 - entry) / entry) * 100 if entry else 0

            rr1 = abs((tp1 - entry) / (sl - entry)) if abs(sl - entry) > 0 else 0

            print(f"--- Rank {i+1} ---")
            print(f"Symbol: {item['Symbol']}")
            print(f"Action: {item['Action']}  |  Confidence: {item['Confidence']}%  |  Readiness: {item['Trade Readiness']}")
            print(f"Entry Quality: {item.get('Entry Quality', 'N/A')}  |  Risk Level: {item.get('Summary', {}).get('Risk Level', 'N/A')}")
            if "News Score" in item:
                print(f"News Score: {item.get('News Score', 0)}  |  Sentiment Score: {item.get('Sentiment Score', 0)}")
            if "VolumeUSDT" in item:
                print(f"24h Volume: {item['VolumeUSDT']:,} USDT")
            print(f"Entry: {smart_price(entry)}")
            print(f"Stop Loss: {smart_price(sl)} ({sl_pct:+.2f}%)")
            print(f"Take Profit: {smart_price(tp1)} ({tp1_pct:+.2f}%)  |  R:R = {rr1:.1f}")
            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Input: {item.get('InputPct', 'N/A')}%")

            if item.get("Macro Risk"):
                print(f"⚠️ Macro Risk Active: {item.get('Macro Event', 'High Impact News')}")

            relevant = item.get("Relevant News", [])
            if relevant:
                print("Relevant News:")
                for r in relevant[:3]:
                    print(f"  {r['source']}: {r['title']} ({r['sentiment']}, impact {r['impact']})")

            print(f"Market Bias: {item['Summary'].get('Market Bias', '')}")
            print(f"Status: {item['Summary'].get('Current Status', '')}")
            print(f"Decision Reason: {item['Summary'].get('Decision Reason', '')}")
            missing = item['Summary'].get('Missing', [])
            if missing:
                print("Missing for Entry:")
                for m in missing:
                    print(f"  - {m}")
            weighted_reasons = item.get("Weighted Reasons", [])
            if weighted_reasons:
                print("Key Reasons:")
                for r in weighted_reasons[:5]:
                    print(f"  {r}")
            print("")

        # جزئیات کامل برای همه فرصت‌ها
        print("\n" + "-" * 75)
        for item in results:
            entry = item.get("Entry", 0)
            sl = item.get("StopLoss", 0)
            tp1 = item.get("TP1", item.get("TakeProfit", 0))

            sl_pct = ((sl - entry) / entry) * 100 if entry else 0
            tp1_pct = ((tp1 - entry) / entry) * 100 if entry else 0
            rr1 = abs((tp1 - entry) / (sl - entry)) if abs(sl - entry) > 0 else 0

            print(f"\nSymbol: {item['Symbol']}")
            print(f"Action: {item['Action']}")
            print(f"Trade Readiness: {item['Trade Readiness']}")
            if "VolumeUSDT" in item:
                print(f"24h Volume: {item['VolumeUSDT']:,} USDT")
            print(f"Entry: {smart_price(entry)}")
            print(f"Stop Loss: {smart_price(sl)} ({sl_pct:+.2f}%)")
            print(f"Take Profit: {smart_price(tp1)} ({tp1_pct:+.2f}%)  |  R:R = {rr1:.1f}")
            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Input: {item.get('InputPct', 'N/A')}%")
            if item.get("Macro Risk"):
                print(f"⚠️ Macro Risk Active: {item.get('Macro Event', '')}")
            print(f"News Score: {item.get('News Score', 0)}  |  Sentiment Score: {item.get('Sentiment Score', 0)}")
            print(f"Reasons: {item.get('Reasons', '')}")
            print(f"Warnings: {item.get('Warnings', '')}")
            print("-" * 75)
