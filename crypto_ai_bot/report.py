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


        table = table.sort_values(
            by="Score",
            ascending=False
        )


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
            "Alignment",
            "RSI",
            "Score",
            "Action"

        ]


        for col in optional_columns:

            if col in table.columns:

                columns.append(col)



        print(

            table[columns].to_string(
                index=False
            )

        )


        print("=" * 140)


        print("\nTop Opportunities:\n")



        for item in results:


            print("-" * 75)


            print(
                f"Symbol      : {item.get('Symbol')}"
            )


            print(
                f"Price       : {item.get('Price')}"
            )


            print(
                f"Trend       : {item.get('Trend')}"
            )


            print(
                f"Strength    : {item.get('Strength')}"
            )



            if "MTF_Signal" in item:

                print(
                    f"MTF Signal  : {item['MTF_Signal']}"
                )



            if "Confidence" in item:

                print(
                    f"Confidence  : {item['Confidence']}%"
                )



            if "Alignment" in item:

                print(
                    f"Alignment   : {item['Alignment']}%"
                )



            print(
                f"RSI         : {item.get('RSI')}"
            )


            print(
                f"Score       : {item.get('Score')}"
            )


            print(
                f"Action      : {item.get('Action')}"
            )



            if "Breakout" in item:

                print(
                    f"Breakout    : {item['Breakout']}"
                )



            if "Support" in item:

                print(
                    f"Support     : {item['Support']}"
                )



            if "Resistance" in item:

                print(
                    f"Resistance  : {item['Resistance']}"
                )



            if "Entry" in item:

                print(
                    f"Entry       : {item['Entry']}"
                )



            if "StopLoss" in item:

                print(
                    f"Stop Loss   : {item['StopLoss']}"
                )



            if "TakeProfit" in item:

                print(
                    f"Take Profit : {item['TakeProfit']}"
                )



            if "RiskReward" in item:

                print(
                    f"Risk/Reward : {item['RiskReward']}"
                )



            if "Reasons" in item:

                print(
                    f"Reasons     : {item['Reasons']}"
                )



            if "Warnings" in item and item["Warnings"]:

                print(
                    f"Warnings    : {item['Warnings']}"
                )



        print("-" * 75)
