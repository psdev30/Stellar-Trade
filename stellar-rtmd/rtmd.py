import asyncio
import httpx
import time
import redis
from resources.api_secrets import *
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.logger_setup import get_logger
import requests as r
import concurrent.futures

logger = get_logger()

headers = {
    'Content-Type': 'application/json'
}

# async def fetch(s, symbol):
#     data_endpoint = "/iex/?tickers={}&token={}"
#     url = tiingo_base_url + data_endpoint
#     async with s.get(url, headers=headers) as r:
#         if r.status != 200:
#             r.raise_for_status()
#         return await r.text()

# async def fetch_all(s, symbols):
#     tasks = []
#     for symbol in symbols:
#         task = asyncio.create_task(fetch(s, symbol))
#         tasks.append(task)
#     res = await asyncio.gather(*tasks)
#     return res

# @logger.catch
# async def main():
#     async with aiohttp.ClientSession() as session:
#         results = await fetch_all(session, ['AAPL', 'GOOG', 'Z'])
#         print(results)

# @logger.catch
# def main():
#     while True:
#         tickers = ",".join(['GOOG', 'Z', 'AAPL'])
#         res = r.get(tiingo_base_url + '/iex/?tickers={}&token={}'.format(tickers, tiingo_api_key)).json()
#         for datapoint in res:
#             print(type(datapoint))
#             print(datapoint)

# Connect to the Redis server
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@logger.catch
async def fetch_market_data(ticker):
    try:
        async with httpx.AsyncClient() as client:
            # Asynchronously get market data for a ticker
            response = await client.get('https://jsonplaceholder.typicode.com/todos')
            # response = await client.get(tiingo_base_url + f'/iex/?tickers={ticker}&token={tiingo_api_key}')
            # response.raise_for_status()
            res = response.json()

            # await generateSignal(ticker, res)
            # Process market data for the ticker
            with concurrent.futures.ProcessPoolExecutor() as executor:
                # Pass the ticker and market data to the executor
                future = executor.submit(generateSignal, ticker, res)

                # Set the flag to indicate that a task is in progress for the ticker
                # redis_client.set(ticker, 1)
                # Add a callback to clear the in-progress flag when the task is complete
                future.add_done_callback(lambda _: print())

    except Exception as e:
        pass
        # Handle exceptions appropriately
        # logger.error(f"Error processing market data for {ticker}: {e}")


def generateSignal(ticker, datapoint):
    # Your logic to generate a signal using the ticker and market data
    print(f'got to generate signal with: {ticker}')
    # logger.info(f"Generating signal for {ticker}: {datapoint}")
    

async def main():
    # List of tickers
    tickers = condensed_secmaster_ticker_list
    # tickers = ['GOOG', 'AAPL', 'Z', 'TSLA', 'NVDA']

    # while True:
    # Use asyncio.gather to run fetch_market_data tasks concurrently
    tasks = [fetch_market_data(ticker) for ticker in tickers]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)