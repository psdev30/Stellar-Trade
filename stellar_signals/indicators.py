from datetime import datetime
import json
import pandas as pd
import requests as r
from resources.api_secrets import *
from resources.ticker_universe import secmaster_ticker_list
from resources.logger_setup import get_logger
import redis


class Indicators():
    def __init__(self) -> None:
        self.logger = get_logger()
        self.headers = {'Content-Type': 'application/json'}
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
        self.redis = redis.StrictRedis(host='stellar.lcfl1t.ng.0001.use2.cache.amazonaws.com', port=6379, password=None, decode_responses=True)

    def macd(self, df, short_window=12, long_window=26, signal_window=9):
        eod_data = df
        if 'adjClose' not in eod_data.columns.tolist():
            return f'False; adjusted close prices are not present'
        # Calculate Short-term EMA
        short_ema = eod_data['adjClose'].ewm(span=short_window, adjust=False).mean()
        # Calculate Long-term EMA
        long_ema = eod_data['adjClose'].ewm(span=long_window, adjust=False).mean()
        # Calculate MACD Line
        macd_line = short_ema - long_ema
        # Calculate Signal Line
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        # Calculate MACD Histogram
        macd_histogram = macd_line - signal_line

        # Create DataFrame with results
        macd_data = pd.DataFrame({
            'MACD': macd_line,
            'Signal_Line': signal_line,
            'MACD_Histogram': macd_histogram
        })

        # Check for MACD and Signal Line crossovers in the last two rows
        last_row = macd_data.iloc[-1]
        second_last_row = macd_data.iloc[-2]
        if second_last_row['MACD'] > second_last_row['Signal_Line'] and last_row['MACD'] < last_row['Signal_Line']:
            return (True, -1)
        elif second_last_row['MACD'] < second_last_row['Signal_Line'] and last_row['MACD'] > last_row['Signal_Line']:
            return (True, 1)
        else:
            return False
    
    def rsi(self, df, window=14):
        df = df['adjClose']

        close_delta = df.diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        
        # Use exponential moving average
        ma_up = up.ewm(com = window - 1, adjust=True, min_periods = window).mean()
        ma_down = down.ewm(com = window - 1, adjust=True, min_periods = window).mean()
            
        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))
        return rsi.iloc[-1]


    def ema(self, df, window=50, smoothing=2):
        prices = df['adjClose'].values
        ema = [sum(prices[:window]) / window]
        for price in prices[window:]:
            ema.append((price * (smoothing / (1 + window))) + ema[-1] * (1 - (smoothing / (1 + window))))
        return ema


    def _get_tiingo_data(self, ticker, start_date):
        url = f'{tiingo_base_url}/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={self.curr_date} \
            &format=json&resampleFreq=daily&sort=date&token={tiingo_api_key}'
        response = r.get(url, headers=self.headers)
        print(type(response.json()), response.json())

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Tiingo API request failed with status code: {response.status_code}")


    def _get_prev_date(self, days_back):
        range = pd.bdate_range(end=self.curr_date, periods=days_back)
        # Get the desired date
        desired_date = range[0]

        # Format the date in "YYYY-MM-DD" format
        formatted_date = desired_date.strftime("%Y-%m-%d")
        return formatted_date

    def cache_daily_historical_data(self):
        for ticker in secmaster_ticker_list:
            start_date = self._get_prev_date(365)
            data = self._get_tiingo_data(ticker, start_date)
            data = json.dumps(data)
            self.redis.hset('daily_historical_data', ticker, data)

hash_key = 'daily_historical_data'
ticker = 'META'
indicators = Indicators()
# indicators.cache_daily_historical_data()
# df = pd.DataFrame(json.loads(indicators.redis.hget(hash_key, ticker)))
# print(df.head())
indicators.redis.delete(hash_key)


