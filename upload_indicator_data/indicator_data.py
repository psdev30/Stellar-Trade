import asyncio
import httpx
from datetime import datetime
import json
import pandas as pd
from resources.api_secrets import *
from resources.ticker_universe import secmaster_ticker_list
import boto3

s3 = boto3.client('s3')
bucket = 'stellar-indicators'


def lambda_handler(event=None, context=None):
    asyncio.run(handler())


async def handler():
    start_date = _get_prev_date(365)
    tasks = [_get_data(ticker, start_date)
             for ticker in secmaster_ticker_list]
    results = await asyncio.gather(*tasks)
    for result in results:
        upload_indicator_data(result)

    return 'All indicator data uploaded to S3 bucket'


def upload_indicator_data(result):
    ticker, df = result
    ema_res = ema(ticker, df)
    rsi_res = rsi(ticker, df)
    data = {'ema': ema_res, 'rsi': rsi_res}
    s3.put_object(
        Bucket=bucket,
        key=ticker,
        Body=json.dumps(data),
        ContentType='application/json',
        ACL='public-read'
    )
    print(f"Daily indicator data uploaded to S3 bucket {bucket}")


async def _get_data(ticker, start_date):
    try:
        async with httpx.AsyncClient() as client:
            url = f'{tiingo_base_url}/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={datetime.now().strftime("%Y-%m-%d")} \
                &format=json&resampleFreq=daily&sort=date&token={tiingo_api_key}'
            response = await client.get(
                url, headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                return ticker, pd.DataFrame(response.json())
            else:
                raise ValueError(
                    f"Tiingo API request failed with status code: {response.status_code}")
    except Exception as e:
        print('Exception: ', e)
        return ticker, None


def _get_prev_date(days_back):
    range = pd.bdate_range(end=datetime.now().strftime(
        "%Y-%m-%d"), periods=days_back)
    # Get the desired date
    desired_date = range[0]

    # Format the date in "YYYY-MM-DD" format
    formatted_date = desired_date.strftime("%Y-%m-%d")
    return formatted_date


def ema(df, window=50, smoothing=2):
    prices = df['adjClose'].values
    ema = [sum(prices[:window]) / window]
    for price in prices[window:]:
        ema.append((price * (smoothing / (1 + window))) +
                   ema[-1] * (1 - (smoothing / (1 + window))))
    return ema


def macd(df, short_window=12, long_window=26, signal_window=9):
    eod_data = df
    if 'adjClose' not in eod_data.columns.tolist():
        return f'False; adjusted close prices are not present'
    # Calculate Short-term EMA
    short_ema = eod_data['adjClose'].ewm(
        span=short_window, adjust=False).mean()
    # Calculate Long-term EMA
    long_ema = eod_data['adjClose'].ewm(
        span=long_window, adjust=False).mean()
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


def rsi(df, window=14):
    df = df['adjClose']

    close_delta = df.diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    # Use exponential moving average
    ma_up = up.ewm(com=window - 1, adjust=True, min_periods=window).mean()
    ma_down = down.ewm(com=window - 1, adjust=True, min_periods=window).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi.iloc[-1]


lambda_handler()