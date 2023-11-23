import asyncio
import aiohttp
import time
from api_secrets import tiingo_base_url, tiingo_api_key, alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.stock import StockHistoricalDataClient
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from logger_setup import get_logger
import requests as r


alpaca_headers = {
    "APCA-API-KEY-ID": alpaca_api_key_id,
    "APCA-API-SECRET-KEY": alpaca_api_secret,
    "Content-Type": "application/msgpack"
}

tiingo_headers = {
    'content': 'application/json'
}

logger = get_logger()

stock_data_client = StockHistoricalDataClient(alpaca_api_key_id, alpaca_api_secret, raw_data=True)


@logger.catch
async def fetch_stock_snapshot(session, symbol):
    quote_endpoint = "/fundamentals/meta"
    url = tiingo_base_url + quote_endpoint + f'?token={tiingo_api_key}'
    async with session.get(url, headers=tiingo_headers) as r:
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


@logger.catch
async def main():
    async with aiohttp.ClientSession() as session:
        results = await fetch_all_snapshots(session, condensed_secmaster_ticker_list)
        # results = clean_data(results)
        print(results)
        return results


start_time = time.time()
# asyncio.run(main())
# res = r.get("https://api.tiingo.com/tiingo/fundamentals/meta?token=9ee8392020ac6d5dd7fb42d38fc7bb5456cda7df",
#             headers=tiingo_headers)
# print(res.text)
end_time = time.time()
print(end_time - start_time)
