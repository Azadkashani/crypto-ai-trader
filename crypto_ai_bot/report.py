"""
Crypto AI Bot v1.2
Advanced Report Engine – Full Details Including PositionRisk Reason, R:R, EV
"""

import pandas as pd

def smart_price(price):
    if price is None: return "N/A"
    if abs(price) < 0.01:
        s = f"{price:.8f}"
        return s.rstrip('0').rstrip('.') if '.' in s else s
    return f"{price:.4f}"

def format_volume(vol):
    if vol is None: return "N/A"
    if vol >= 1e6:
        return f"{vol/1e6:.1f}M"
    elif vol >= 1e3:
        return f"{vol/1e3:.0f}K"
    return f"{vol:.0f}"

class ReportEngine:
    @staticmethod
    def show(results):
        if not results: print("No Data"); return

        table = pd.DataFrame(results)
        table = table.sort_values(by="Trade Readiness", ascending=False)

        if "VolumeUSDT" in table.columns:
            table["VolumeUSDT"] = table["VolumeUSDT"].apply(format_volume)

        print("\n" + "=" * 140)
        print("CRYPTO AI BOT MARKET SCANNER v1.2")
        print("=" * 140)

        columns = [
            "Symbol", "Price", "VolumeUSDT", "Trend", "Strength", "MTF_Signal",
            "Confidence", "RSI", "News Score", "Sentiment Score",
            "Score", "Action", "Market Signal", "Trade Valid",
            "PositionRisk", "ExecutionType", "ExecutionQuality", "ExpectedValue",
            "Entry Quality", "Trade Readiness", "Leverage"
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
            sl_pct = ((sl - entry) / entry) * 100 if entry else 0

            print(f"--- Rank {i+1} ---")
            print(f"Symbol: {item['Symbol']}")
            print(f"Market Signal: {item.get('Market Signal', 'N/A')}")
            print(f"Action: {item['Action']}  |  Trade Valid: {item.get('Trade Valid', False)}")
            print(f"Confidence: {item['Confidence']}%  |  Readiness: {item['Trade Readiness']}")
            if "VolumeUSDT" in item:
                print(f"24h Volume: {item['VolumeUSDT']} USDT")
            print(f"Entry: {smart_price(entry)}")
            print(f"Stop Loss: {smart_price(sl)} ({sl_pct:+.2f}%)")

            targets = item.get("Targets", [])
            if targets:
                print("Targets:")
                for t in targets:
                    print(f"  {t['label']}: {smart_price(t['price'])} ({t['pct']:+.2f}%) | R:R={t['rr']} | Prob={t['probability']}")
            else:
                print("Take Profit: N/A")

            print(f"Position Risk: {item.get('PositionRisk', 'N/A')}")
            if item.get('PositionRiskReason'):
                print(f"  Reason: {item['PositionRiskReason']}")
            print(f"Execution Type: {item.get('ExecutionType', 'N/A')}")
            print(f"Execution Quality: {item.get('ExecutionQuality', 'N/A')}%")
            print(f"Expected Value: {item.get('ExpectedValue', 'N/A')}")

            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Risk/Reward: {item.get('RiskReward', 'N/A')}")

            summary = item.get("Summary", {})
            print(f"Status: {summary.get('Current Status', '')}")
            weighted_reasons = item.get("Weighted Reasons", [])
            if weighted_reasons:
                print("Key Reasons:")
                for r in weighted_reasons[:5]:
                    print(f"  {r}")
            print("")

        print("\n" + "-" * 75)
        for item in results:
            entry = item.get("Entry", 0)
            sl = item.get("StopLoss", 0)
            sl_pct = ((sl - entry) / entry) * 100 if entry else 0

            print(f"\nSymbol: {item['Symbol']}")
            print(f"Market Signal: {item.get('Market Signal', '')}")
            print(f"Action: {item['Action']}  |  Trade Valid: {item.get('Trade Valid', False)}")
            if "VolumeUSDT" in item:
                print(f"24h Volume: {item['VolumeUSDT']} USDT")
            print(f"Entry: {smart_price(entry)}")
            print(f"Stop Loss: {smart_price(sl)} ({sl_pct:+.2f}%)")
            targets = item.get("Targets", [])
            if targets:
                print("Targets:")
                for t in targets:
                    print(f"  {t['label']}: {smart_price(t['price'])} ({t['pct']:+.2f}%) | R:R={t['rr']} | Prob={t['probability']}")
            print(f"Position Risk: {item.get('PositionRisk', 'N/A')}")
            if item.get('PositionRiskReason'):
                print(f"  Reason: {item['PositionRiskReason']}")
            print(f"Execution Type: {item.get('ExecutionType', 'N/A')}")
            print(f"Execution Quality: {item.get('ExecutionQuality', 'N/A')}%")
            print(f"Expected Value: {item.get('ExpectedValue', 'N/A')}")
            print(f"Leverage: {item.get('Leverage', 'N/A')}x")
            print(f"Risk/Reward: {item.get('RiskReward', 'N/A')}")
            print(f"Reasons: {item.get('Reasons', '')}")
            print(f"Warnings: {item.get('Warnings', '')}")
            print("-" * 75)
