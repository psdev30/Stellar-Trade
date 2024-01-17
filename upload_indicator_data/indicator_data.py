import os
import json
import boto3
import pandas as pd
import requests as r
from decimal import Decimal
from datetime import datetime
from sentiment_analysis import SentimentAnalysis

sentiment_analysis = SentimentAnalysis()

db = boto3.resource('dynamodb')
indicator_table = db.Table('stellar-indicator-data')
ref_data_table = db.Table('stellar-reference-data')


sns = boto3.client('sns')
sns_topic_arn = 'arn:aws:sns:us-east-2:921025392800:update-indicator-cache'
sns_message = "Triggering cache indicator data Lambda function"


def lambda_handler(event, context):
    try:
        key = {'reference_data_type': 'secmaster_full'}
        response = ref_data_table.get_item(Key=key)
        tickers = response['Item']['ListAttribute']
        for ticker in tickers:
            upload_indicator_data(ticker)
    except Exception as e:
        return f'Exception here: {e}'

    response = sns.publish(
        TopicArn=sns_topic_arn,
        Message=sns_message,
        Subject="Lambda Notification",
    )
    print(f"SNS Notification sent: {response}")
    return "Daily indicator data uploaded to DynamoDB table & triggered caching Lambda function"


def upload_indicator_data(ticker):
    start_date = _get_prev_date(365)
    df = _get_data(ticker, start_date)
    ema_res = ema(df)[-1]
    rsi_res = rsi(df)
    news = sentiment_analysis.analyze_sentiment(ticker=ticker)
    item = {'ticker': ticker, 'ema': Decimal(str(ema_res)), 'rsi': Decimal(str(rsi_res)), 'news': Decimal(str(news))}
    indicator_table.put_item(
       Item=item
    )


def _get_data(ticker, start_date):
    try:
        url = f'{os.environ.get("tiingo_base_url")}/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={datetime.now().strftime("%Y-%m-%d")} \
            &format=json&resampleFreq=daily&sort=date&token={os.environ.get("tiingo_api_key")}'
        response = r.get(url, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            raise ValueError(
                f"Tiingo API request failed with status code: {response.status_code}")
    except Exception as e:
        print('Exception: ', e)
        return None


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