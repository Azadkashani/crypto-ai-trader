"""
Crypto AI Bot v4
Report Engine
"""

import pandas as pd


class ReportEngine:

    @staticmethod
    def show(results):

        if len(results) == 0:
            print("No Data")
            return

        table = pd.DataFrame(results)

        table = table.sort_values(
            by="Score",
            ascending=False
        )

        print("\n")
        print("=" * 100)
        print("CRYPTO AI BOT MARKET SCANNER")
        print("=" * 100)

        print(
            table[
                [
                    "Symbol",
                    "Price",
                    "Trend",
                    "Strength",
                    "RSI",
                    "Score",
                    "Action"
                ]
            ].to_string(index=False)
        )

        print("=" * 100)
