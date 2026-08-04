"""
Crypto AI Bot v1.2
Advanced Report Engine – Displays PositionSizePct instead of InputPct
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
        table = table.sort_values(by="TradeQualityScore", ascending=False)

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
            "TradeQualityScore", "Entry Quality", "Trade Readiness", "Leverage"
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
                    lbl = t.get("label", "TP")
                    price = t.get("price", 0)
                    pct = t.get("pct", 0.0)
                    rr = t.get("rr", 0.0)
                    prob = t.get("probability", 0.0)
                    print(f"  {lbl}: {smart_price(price)} ({pct:+.2f}%) | R:R={rr} | Prob={prob}")

            invalid = item.get("InvalidTargets", [])
            if invalid and not item.get("Trade Valid"):
                print("Invalid Targets (R:R too low or probability insufficient):")
                for t in invalid:
                    lbl = t.get("label", "TP")
                    price = t.get("price", 0)
                    pct = t.get("pct", 0.0)
                    rr = t.get("rr", 0.0)
                    prob = t.get("probability", 0.0)
                    print(f"  {lbl}: {smart_price(price)} ({pct:+.2f}%) | R:R={rr} | Prob={prob}")

            if item.get("Trade Valid"):
                print(f"Position Risk: {item.get('PositionRisk', 'N/A')}")
                if item.get('PositionRiskReason'):
                    print(f"  Reason: {item['PositionRiskReason']}")
                print(f"Position Size: {item.get('PositionSize', 'N/A')} ({item.get('PositionSizePct', 'N/A')})")
                print(f"Risk Amount: {item.get('RiskAmount', 'N/A')} USDT")
                print(f"Risk Level: {item.get('RiskLevel', 'N/A')}")
                print(f"Execution Type: {item.get('ExecutionType', 'N/A')}")
                print(f"Execution Quality: {item.get('ExecutionQuality', 'N/A')}%")
                print(f"Liquidity Risk: {item.get('LiquidityRisk', 'N/A')}")
                ev_str = item.get("ExpectedValue", "N/A")
                print(f"Expected Value: {ev_str}")
                print(f"Leverage: {item.get('Leverage', 'N/A')}x")
                print(f"Risk/Reward: {item.get('RiskReward', 'N/A')}")
                print(f"Trade Quality: {item.get('TradeQualityScore', 'N/A')}%")
            else:
                print("Status: Waiting for confirmation.")
                watch_info = item.get("WatchInfo", {})
                if watch_info:
                    print("Watch Details:")
                    for k, v in watch_info.items():
                        print(f"  {k}: {v}")

            summary = item.get("Summary", {})
            print(f"Current Status: {summary.get('Current Status', '')}")
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
                    lbl = t.get("label", "TP")
                    price = t.get("price", 0)
                    pct = t.get("pct", 0.0)
                    rr = t.get("rr", 0.0)
                    prob = t.get("probability", 0.0)
                    print(f"  {lbl}: {smart_price(price)} ({pct:+.2f}%) | R:R={rr} | Prob={prob}")

            invalid = item.get("InvalidTargets", [])
            if invalid and not item.get("Trade Valid"):
                print("Invalid Targets (R:R too low or probability insufficient):")
                for t in invalid:
                    lbl = t.get("label", "TP")
                    price = t.get("price", 0)
                    pct = t.get("pct", 0.0)
                    rr = t.get("rr", 0.0)
                    prob = t.get("probability", 0.0)
                    print(f"  {lbl}: {smart_price(price)} ({pct:+.2f}%) | R:R={rr} | Prob={prob}")

            if item.get("Trade Valid"):
                print(f"Position Risk: {item.get('PositionRisk', 'N/A')}")
                if item.get('PositionRiskReason'):
                    print(f"  Reason: {item['PositionRiskReason']}")
                print(f"Position Size: {item.get('PositionSize', 'N/A')} ({item.get('PositionSizePct', 'N/A')})")
                print(f"Risk Amount: {item.get('RiskAmount', 'N/A')} USDT")
                print(f"Risk Level: {item.get('RiskLevel', 'N/A')}")
                print(f"Execution Type: {item.get('ExecutionType', 'N/A')}")
                print(f"Execution Quality: {item.get('ExecutionQuality', 'N/A')}%")
                print(f"Liquidity Risk: {item.get('LiquidityRisk', 'N/A')}")
                ev_str = item.get("ExpectedValue", "N/A")
                print(f"Expected Value: {ev_str}")
                print(f"Leverage: {item.get('Leverage', 'N/A')}x")
                print(f"Risk/Reward: {item.get('RiskReward', 'N/A')}")
                print(f"Trade Quality: {item.get('TradeQualityScore', 'N/A')}%")
            else:
                print("Status: Waiting for confirmation.")
                watch_info = item.get("WatchInfo", {})
                if watch_info:
                    print("Watch Details:")
                    for k, v in watch_info.items():
                        print(f"  {k}: {v}")

            print(f"Reasons: {item.get('Reasons', '')}")
            print(f"Warnings: {item.get('Warnings', '')}")
            print("-" * 75)
