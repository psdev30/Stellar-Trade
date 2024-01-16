import os
import json
import redis
import boto3


db = boto3.resource('dynamodb')
indicator_table = db.Table('stellar-indicator-data')
ref_data_table = db.Table('stellar-reference-data')

redis = redis.StrictRedis(
    host=os.environ.get('elasticache_host'), 
    port=int(os.environ.get('elasticache_port')), 
    decode_responses=True
)


def lambda_handler(event, context):
    return cache_daily_historical_data()


def cache_daily_historical_data():
    key = {'reference_data_type': 'secmaster_full'}
    response = ref_data_table.get_item(Key=key)
    tickers = response['Item']['ListAttribute']
    for ticker in tickers:
        key = {'ticker': ticker}
        response = indicator_table.get_item(Key=key)
        data = json.dumps(response['Item'], default=str)
        redis.hset('daily_indicator_data', ticker, data)
    return True, 'All indicator data uploaded to Redis'
