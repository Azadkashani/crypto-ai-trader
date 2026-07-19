"""
Crypto AI Bot v5.1
Report Engine
"""

import pandas as pd


class ReportEngine:

    @staticmethod
    def show(results):

        if not results:
            print("No Data")
            return

        table = pd.DataFrame(results)

        table = table.sort_values(
            by="Score",
            ascending=False
        )

        print("\n")
        print("=" * 130)
        print("CRYPTO AI BOT MARKET SCANNER")
        print("=" * 130)

        columns = [
            "Symbol",
            "Price",
            "Trend",
            "Strength",
        ]

        if "Confidence" in table.columns:
            columns.append("Confidence")

        if "Alignment" in table.columns:
            columns.append("Alignment")

        columns.extend([
            "RSI",
            "Score",
            "Action"
        ])

        print(
            table[columns].to_string(
                index=False
            )
        )

        print("=" * 130)

        print("\nTop Opportunities:\n")

        for item in results:

            print("-" * 70)

            print(f"Symbol      : {item['Symbol']}")
            print(f"Price       : {item['Price']}")
            print(f"Trend       : {item['Trend']}")
            print(f"Strength    : {item['Strength']}")

            if "Confidence" in item:
                print(f"Confidence  : {item['Confidence']}%")

            if "Alignment" in item:
                print(f"Alignment   : {item['Alignment']}%")

            print(f"RSI         : {item['RSI']}")
            print(f"Score       : {item['Score']}")
            print(f"Action      : {item['Action']}")

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

            if "Reasons" in item:
                print(f"Reasons     : {item['Reasons']}")

        print("-" * 70)
