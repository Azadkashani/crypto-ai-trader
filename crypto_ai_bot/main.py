"""
Crypto AI Bot v1.0
Signal-Only Mode – Gate.io Futures
"""

import time
from scanner import MarketScanner
from report import ReportEngine
from config import SCAN_INTERVAL_MINUTES


def main():
    print("Starting Crypto AI Bot (Signal-Only Mode)...")
    scanner = MarketScanner()

    while True:
        print("\nScanning Market...")
        results = scanner.scan()

        if results:
            ReportEngine.show(results)
        else:
            print("No results.")

        print(f"\nNext scan in {SCAN_INTERVAL_MINUTES} minutes...")
        time.sleep(SCAN_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
