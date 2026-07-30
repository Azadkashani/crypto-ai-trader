"""
Crypto AI Bot v5.7
Advanced Report Engine with Ranking
"""

import pandas as pd


class ReportEngine:

    @staticmethod
    def show(results):
        if not results:
            print("No Data")
            return

        table = pd.DataFrame(results)
        table = table.sort_values(by="Trade Readiness", ascending=False)

        print("\n")
        print("=" * 140)
        print("CRYPTO AI BOT MARKET SCANNER v5.7")
        print("=" * 140)

        columns = [
            "Symbol",
            "Price",
            "Trend",
            "Strength",
            "MTF_Signal",
            "Confidence",
            "RSI",
            "Score",
            "Action",
            "Entry Quality",
            "Trade Readiness"
        ]
        # select only existing columns
        cols = [c for c in columns if c in table.columns]
        print(table[cols].to_string(index=False))
        print("=" * 140)
        print("\n🏆 Top Opportunities Ranking:\n")

        top_n = min(3, len(results))
        for i in range(top_n):
            item = results[i]
            print(f"--- Rank {i+1} ---")
            print(f"Symbol: {item['Symbol']}")
            print(f"Action: {item['Action']}  |  Confidence: {item['Confidence']}%  |  Readiness: {item['Trade Readiness']}")
            print(f"Entry Quality: {item.get('Entry Quality', 'N/A')}  |  Risk Level: {item.get('Summary', {}).get('Risk Level', 'N/A')}")
            print(f"Market Bias: {item['Summary'].get('Market Bias', '')}")
            print(f"Status: {item['Summary'].get('Current Status', '')}")
            print(f"Decision Reason: {item['Summary'].get('Decision Reason', '')}")
            missing = item['Summary'].get('Missing', [])
            if missing:
                print("Missing for Entry:")
                for m in missing:
                    print(f"  - {m}")
            # نمایش دلایل وزن‌دار
            weighted_reasons = item.get("Weighted Reasons", [])
            if weighted_reasons:
                print("Key Reasons:")
                for r in weighted_reasons[:5]:
                    print(f"  {r}")
            print("")

        # نمایش جزئیات کامل برای همه فرصت‌ها (مانند قبل)
        print("\n" + "-" * 75)
        for item in results:
            print(f"\nSymbol: {item['Symbol']}")
            # ... (باقی چاپ همانطور که بود)
            print(f"Action: {item['Action']}")
            print(f"Trade Readiness: {item['Trade Readiness']}")
            # ...
