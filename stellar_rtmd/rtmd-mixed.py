import asyncio
import concurrent.futures
import time
import httpx
from resources.logger_setup import get_logger
from resources.api_secrets import *
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.ticker_universe import secmaster_ticker_list
import redis

# Connect to the Redis server
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

logger = get_logger()

@logger.catch
async def fetch_market_data(ticker):
    try:
        async with httpx.AsyncClient() as client:
            # Asynchronously get market data for a ticker
            response = await client.get('https://jsonplaceholder.typicode.com/todos')
            # response = await client.get(tiingo_base_url + f'/iex/?tickers={ticker}&token={tiingo_api_key}')
            # response.raise_for_status()
            market_data = response.json()

            return ticker, market_data

    except Exception as e:
        # Handle exceptions appropriately
        logger.error(f"Error processing market data for {ticker}: {e}")
        return ticker, None

def generate_signal(ticker_data):
    ticker, market_data = ticker_data
    if market_data:
        logger.info(f"Generating signal for {ticker}: ")
    else:
        logger.warning(f"Market data for {ticker} is None. Signal generation skipped.")
    

def generate_signal_parallel(ticker_data):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Use ProcessPoolExecutor for parallel execution of signal generation
        executor.map(generate_signal, ticker_data)
        # add code to only call it if there isn't an existing process later

async def main():
    # List of tickers
    tickers = condensed_secmaster_ticker_list
    tickers = secmaster_ticker_list

    # Use asyncio.gather to run fetch_market_data tasks concurrently
    tasks = [fetch_market_data(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks)

    # Use ProcessPoolExecutor for parallel signal generation
    generate_signal_parallel(results)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
