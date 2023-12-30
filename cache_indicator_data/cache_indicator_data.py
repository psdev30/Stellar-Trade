import os
import redis
import boto3
from ticker_universe import secmaster_ticker_list

s3_client = boto3.client('s3')

redis = redis.StrictRedis(
    host=os.environ.get('elasticache_host'), port=int(os.environ.get('elasticache_port')), decode_responses=True)


def lambda_handler(event, context):
    return cache_daily_historical_data()


def cache_daily_historical_data():
    for ticker in secmaster_ticker_list:
        response = s3_client.get_object(Bucket=os.environ.get('bucket_name'), Key=ticker)
        data = response['Body'].read().decode('utf-8')
        redis.hset('daily_indicator_data', ticker, data)
    return True, 'All indicator data uploaded to Redis'
