"""
Crypto AI Bot v4
Main Program
"""

from scanner import MarketScanner
from report import ReportEngine


def main():

    print("Starting Crypto AI Bot...")
    print("Scanning Market...\n")

    scanner = MarketScanner()

    results = scanner.scan()

    ReportEngine.show(results)


if __name__ == "__main__":
    main()
