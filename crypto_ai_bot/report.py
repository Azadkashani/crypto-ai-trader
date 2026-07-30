"""
Crypto AI Bot v5.7
Advanced Report Engine
"""

import pandas as pd


class ReportEngine:

    @staticmethod
    def show(results):
        if not results:
            print("No Data")
            return

        table = pd.DataFrame(results)
        table = table.sort_values(by="Score", ascending=False)

        print("\n")
        print("=" * 140)
        print("CRYPTO AI BOT MARKET SCANNER v5.7")
        print("=" * 140)

        columns = [
            "Symbol",
            "Price",
            "Trend",
            "Strength",
        ]
        optional_columns = [
            "MTF_Signal",
            "Confidence",
            "RSI",
            "Score",
            "Action",
            "Entry Quality",
            "Trade Readiness"
        ]
        for col in optional_columns:
            if col in table.columns:
                columns.append(col)

        print(
            table[columns].to_string(index=False)
        )
        print("=" * 140)
        print("\nTop Opportunities:\n")

        for item in results:
            print("-" * 75)
            print(f"Symbol      : {item.get('Symbol')}")
            print(f"Price       : {item.get('Price')}")
            print(f"Trend       : {item.get('Trend')}")
            print(f"Strength    : {item.get('Strength')}")

            if "MTF_Signal" in item:
                print(f"MTF Signal  : {item['MTF_Signal']}")
            if "Base Score" in item:
                print(f"Base Score  : {item['Base Score']}")
            if "MTF Bonus" in item:
                print(f"MTF Bonus   : {item['MTF Bonus']}")
            if "Confidence" in item:
                print(f"Confidence  : {item['Confidence']}%")
            print(f"RSI         : {item.get('RSI')}")
            print(f"Score       : {item.get('Score')}")
            print(f"Action      : {item.get('Action')}")
            if "Entry Quality" in item:
                print(f"Entry Quality: {item['Entry Quality']}")
            if "Trade Readiness" in item:
                print(f"Trade Readiness: {item['Trade Readiness']}")

            if "Volume Breakout" in item:
                print(f"Volume Breakout: {item['Volume Breakout']}")

            if "Support" in item:
                print(f"Support     : {item['Support']}")
            if "Resistance" in item:
                print(f"Resistance  : {item['Resistance']}")
            if "Entry" in item:
                print(f"Entry       : {item['Entry']}")
            if "StopLoss" in item:
                print(f"Stop Loss   : {item['StopLoss']}")
            if "TakeProfit" in item:
                print(f"Take Profit : {item['TakeProfit']}")

            # Weighted Reasons
            weighted_reasons = item.get("Weighted Reasons", [])
            if weighted_reasons:
                print("Reasons (weighted):")
                for r in weighted_reasons:
                    print(f"  {r}")

            # Weighted Warnings
            weighted_warnings = item.get("Weighted Warnings", [])
            if weighted_warnings:
                print("Warnings (weighted):")
                for w in weighted_warnings:
                    print(f"  {w}")

            # Summary
            summary = item.get("Summary")
            if summary:
                print(f"\nMarket Bias: {summary.get('Market Bias', '')}")
                why_not = summary.get("Why Not Buy?", [])
                if why_not:
                    print("Why Not Buy?")
                    for reason in why_not:
                        print(f"  - {reason}")
                print(f"Current Status: {summary.get('Current Status', '')}")
                print(f"Next Trigger: {summary.get('Next Trigger', '')}")

            # Watch Reason
            watch_details = item.get("Watch Reason")
            if watch_details:
                print("Watch Reason:")
                for line in watch_details:
                    print(f"  {line}")

            print("-" * 75)
