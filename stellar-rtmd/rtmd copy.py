import asyncio
import aiohttp
import time
from resources.api_secrets import alpaca_data_base_url, alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.logger_setup import get_logger

logger = get_logger()

headers = {
    "APCA-API-KEY-ID": alpaca_api_key_id,
    "APCA-API-SECRET-KEY": alpaca_api_secret,
}

stock_data_client = StockHistoricalDataClient(alpaca_api_key_id, alpaca_api_secret, raw_data=True)

@logger.catch
def get_stock_snapshot(symbol):
    while True:
        try:
            res = stock_data_client.get_stock_snapshot(request_params=StockSnapshotRequest(symbol_or_symbols=symbol))
            return res  # res is a plain Python dict
        except Exception as e:
            print(e)

async def fetch(s, symbol):
    quote_endpoint = "/v2/stocks/{}/quotes".format(symbol)
    url = alpaca_data_base_url + quote_endpoint
    async with s.get(url, headers=headers) as r:
        if r.status != 200:
            r.raise_for_status()
        return await r.text()

async def fetch_all(s, symbols):
    tasks = []
    for symbol in symbols:
        task = asyncio.create_task(fetch(s, symbol))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res

@logger.catch
async def main():
    async with aiohttp.ClientSession() as session:
        results = await fetch_all(session, condensed_secmaster_ticker_list)
        print(results)

start_time = time.time()
asyncio.run(main())
end_time = time.time()
print(end_time - start_time)
