import json
from resources.logger_setup import get_logger
from resources.api_secrets import *
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.ticker_universe import secmaster_ticker_list
from datetime import datetime
import pandas as pd
import requests as r


class Indicators():
    def __init__(self) -> None:
        self.logger = get_logger()
        self.headers = {'Content-Type': 'application/json'}
        self.curr_date = datetime.now().strftime("%Y-%m-%d")

    def macd(self, ticker, short_window=12, long_window=26, signal_window=9):
        start_date = self._get_prev_date(35)
        close_prices = r.get(tiingo_base_url + f'/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={self.curr_date} \
            &format=json&resampleFreq=daily&sort=date \
            &columns=adjClose&token={tiingo_api_key}', headers=self.headers).json()
            
        eod_data = pd.DataFrame(close_prices)
        if 'adjClose' not in eod_data.columns.tolist():
            return f'Stop here: {ticker}'
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

    def _get_prev_date(self, days_back):
        range = pd.bdate_range(end=self.curr_date, periods=days_back)
        # Get the desired date
        desired_date = range[0]

        # Format the date in "YYYY-MM-DD" format
        formatted_date = desired_date.strftime("%Y-%m-%d")
        return formatted_date


indicators = Indicators()
res = indicators.macd('AAPL')
print(res)
