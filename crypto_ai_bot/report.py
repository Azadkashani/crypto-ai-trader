"""
Crypto AI Bot v5.7
MTF Report Engine
"""


def print_report(results):

    print("\n")
    print("=" * 130)
    print("CRYPTO AI BOT MARKET SCANNER")
    print("=" * 130)


    print(
        f"{'Symbol':<12}"
        f"{'Price':>12}"
        f"{'Trend':>12}"
        f"{'Strength':>12}"
        f"{'Confidence':>14}"
        f"{'RSI':>8}"
        f"{'Score':>8}"
        f"{'Action':>12}"
    )


    for r in results:


        print(
            f"{r['Symbol']:<12}"
            f"{r['Price']:>12}"
            f"{r['Trend']:>12}"
            f"{r['Strength']:>12}"
            f"{str(r['Confidence'])+'%':>14}"
            f"{r['RSI']:>8}"
            f"{r['Score']:>8}"
            f"{r['Action']:>12}"
        )



    print("=" * 130)


    print("\nTop Opportunities:\n")


    for r in results:


        print("-" * 70)


        print(
            f"""
Symbol       : {r['Symbol']}
Price        : {r['Price']}
Trend        : {r['Trend']}
Strength     : {r['Strength']}

MTF Signal   : {r.get('MTF Signal','N/A')}
MTF Score    : {r.get('MTF Score','N/A')}

Confidence   : {r['Confidence']}%
RSI          : {r['RSI']}
Score        : {r['Score']}
Action       : {r['Action']}

Support      : {r['Support']}
Resistance   : {r['Resistance']}

Entry        : {r['Entry']}
Stop Loss    : {r['StopLoss']}
Take Profit  : {r['TakeProfit']}

Breakout     : {r.get('Breakout',False)}

Reasons      : {r['Reasons']}

Warnings     : {r.get('Warnings','')}
"""
        )


        if "MTF Details" in r:

            print("\nMTF Details:")

            for tf, signal in r["MTF Details"].items():

                print(
                    f"  {tf} : {signal}"
                )


    print("-" * 70)
