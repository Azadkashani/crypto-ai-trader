"""
Crypto AI Bot v5.7
Advanced Report Engine (with Entry, SL, TP, Leverage, R/R, and percentages)
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
            "Symbol", "Price", "Trend", "Strength", "MTF_Signal",
            "Confidence", "RSI", "News Score", "Sentiment Score",
            "Score", "Action", "Entry Quality", "Trade Readiness", "Leverage"
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
            tp = item.get("TakeProfit", 0)

            # محاسبه درصد حد ضرر و سود نسبت به قیمت ورود
            sl_pct = ((sl - entry) / entry) * 100 if entry else 0
            tp_pct = ((tp - entry) / entry) * 100 if entry else 0

            print(f"--- Rank {i+1} ---")
            print(f"Symbol: {item['Symbol']}")
            print(f"Action: {item['Action']}  |  Confidence: {item['Confidence']}%  |  Readiness: {item['Trade Readiness']}")
            print(f"Entry Quality: {item.get('Entry Quality', 'N/A')}  |  Risk Level: {item.get('Summary', {}).get('Risk Level', 'N/A')}")
            if "News Score" in item:
                print(f"News Score: {item['News Score']}  |  Sentiment Score: {item.get('Sentiment Score', 0)}")
            print(f"Entry: {entry}")
            print(f"Stop Loss: {sl} ({sl_pct:+.2f}%)")
            print(f"Take Profit: {tp} ({tp_pct:+.2f}%)")
            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Risk/Reward: 2.0")
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
            weighted_warnings = item.get("Weighted Warnings", [])
            if weighted_warnings:
                print("Key Warnings:")
                for w in weighted_warnings[:3]:
                    print(f"  {w}")
            print("")

        # جزئیات کامل برای همه فرصت‌ها
        print("\n" + "-" * 75)
        for item in results:
            entry = item.get("Entry", 0)
            sl = item.get("StopLoss", 0)
            tp = item.get("TakeProfit", 0)
            sl_pct = ((sl - entry) / entry) * 100 if entry else 0
            tp_pct = ((tp - entry) / entry) * 100 if entry else 0

            print(f"\nSymbol: {item['Symbol']}")
            print(f"Action: {item['Action']}")
            print(f"Trade Readiness: {item['Trade Readiness']}")
            print(f"Entry: {entry}")
            print(f"Stop Loss: {sl} ({sl_pct:+.2f}%)")
            print(f"Take Profit: {tp} ({tp_pct:+.2f}%)")
            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Risk/Reward: 2.0")
            if "News Score" in item:
                print(f"News Score: {item['News Score']}")
                print(f"Sentiment Score: {item['Sentiment Score']}")
            print(f"Reasons: {item.get('Reasons', '')}")
            print(f"Warnings: {item.get('Warnings', '')}")
            print("-" * 75)
