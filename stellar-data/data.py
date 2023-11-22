import asyncio
import aiohttp
import time
from api_secrets import alpaca_data_base_url, alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.stock import StockHistoricalDataClient
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from confluent_kafka import Producer
from logger_setup import get_logger

headers = {
    "APCA-API-KEY-ID": alpaca_api_key_id,
    "APCA-API-SECRET-KEY": alpaca_api_secret,
    "Content-Type": "application/msgpack"
}

logger = get_logger()

def _get_kafka_producer():
    conf = {
        'bootstrap.servers': 'your_kafka_broker',
        'client.id': 'python-producer'
    }
    return Producer(conf)

stock_data_client = StockHistoricalDataClient(alpaca_api_key_id, alpaca_api_secret, raw_data=True)

@logger.catch
async def fetch_stock_snapshot(session, symbol):
    quote_endpoint = "/v2/stocks/{}/snapshot".format(symbol)
    url = alpaca_data_base_url + quote_endpoint
    async with session.get(url, headers=headers) as r:
        if r.status != 200:
            r.raise_for_status()
        return await r.text()

            
async def fetch_all_snapshots(session, symbols):
    tasks = []
    for symbol in symbols:
        task = asyncio.create_task(fetch_stock_snapshot(session, symbol))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res

def clean_data(results):
    print(results)

def publish_to_kafka(results):
    producer = _get_kafka_producer()
    

@logger.catch
async def main():
    async with aiohttp.ClientSession() as session:
        results = await fetch_all_snapshots(session, condensed_secmaster_ticker_list)
        results = clean_data(results)


start_time = time.time()
asyncio.run(main())
end_time = time.time()
print(end_time - start_time)
