def load_data(self):
        import os
        import pandas as pd

        # ابتدا سعی می‌کنیم داده‌ها را از فایل‌های CSV محلی بخوانیم
        for sym in self.symbols:
            # نام فایل بر اساس نماد (مثلاً BTCUSDT_1h.csv)
            base_name = sym.replace("/", "").replace(":", "")  # BTC/USDT -> BTCUSDT
            csv_filename = f"{base_name}_{self.timeframe}.csv"  # مثلاً BTCUSDT_1h.csv
            csv_path = os.path.join(self.output_dir, csv_filename)  # جستجو در پوشه output یا اصلی
            if not os.path.exists(csv_path):
                csv_path = csv_filename  # همان پوشهٔ جاری

            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    print(f"Loaded {csv_path}")
                    # تشخیص ستون‌ها: ممکن است timestamp/time, open, high, low, close, volume
                    # سعی می‌کنیم نگاشت خودکار انجام دهیم
                    col_map = {
                        'timestamp': 'time', 'date': 'time', 'datetime': 'time',
                        'open': 'open', 'Open': 'open',
                        'high': 'high', 'High': 'high',
                        'low': 'low', 'Low': 'low',
                        'close': 'close', 'Close': 'close',
                        'volume': 'volume', 'Volume': 'volume', 'vol': 'volume'
                    }
                    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
                    if 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'])
                    else:
                        # اگر ستون زمان وجود نداشته باشد، فرض می‌کنیم ردیف‌ها پشت‌سرهم هستند
                        print("Warning: no time column found, assuming sequential rows")
                        df['time'] = pd.date_range(start=self.start_date, periods=len(df), freq=self.timeframe)
                    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                    df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                    if df.empty:
                        print(f"No data in range for {sym} in CSV")
                        continue
                    df = df.reset_index(drop=True)
                    self.data[sym] = df
                    self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                    print(f"Prepared {len(df)} candles for {sym}")
                    continue
                except Exception as e:
                    print(f"Error reading CSV for {sym}: {e}")

            # اگر CSV نبود، سراغ API یا yfinance برو (کد قبلی)
            if self.use_mock:
                df = self._generate_mock_data(sym)
                self.data[sym] = df
                self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                print(f"Generated {len(df)} mock candles for {sym}")
                continue

            # تلاش با API صرافی (در صورت وجود)
            if self.exchange is not None:
                try:
                    ohlcv = self.exchange.fetch_ohlcv(
                        sym,
                        timeframe=self.timeframe,
                        since=int(self.start_date.timestamp() * 1000),
                        limit=1000
                    )
                    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                    df['time'] = pd.to_datetime(df['time'], unit='ms')
                    df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                    if not df.empty:
                        df = df.reset_index(drop=True)
                        self.data[sym] = df
                        self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                        print(f"Loaded {len(df)} candles for {sym} from API")
                        continue
                except Exception as e:
                    print(f"API failed for {sym}: {e}")

            # fallback: yfinance
            try:
                import yfinance as yf
                ticker = sym.replace("/", "-")
                yf_ticker = yf.Ticker(ticker)
                df = yf_ticker.history(
                    start=self.start_date.strftime('%Y-%m-%d'),
                    end=(self.end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    interval=self.timeframe
                )
                if not df.empty:
                    df.reset_index(inplace=True)
                    df.rename(columns={'Date': 'time', 'Datetime': 'time', 'Open': 'open', 'High': 'high',
                                       'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
                    df['time'] = pd.to_datetime(df['time'])
                    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                    df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                    if df.empty:
                        continue
                    df = df.reset_index(drop=True)
                    self.data[sym] = df
                    self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                    print(f"Loaded {len(df)} candles for {sym} from yfinance")
            except Exception as e:
                print(f"yfinance failed for {sym}: {e}")
