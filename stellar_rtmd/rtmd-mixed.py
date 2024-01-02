import asyncio
import concurrent.futures
import time
import httpx
from resources.logger_setup import get_logger
from resources.api_secrets import *
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.ticker_universe import secmaster_ticker_list
from stellar_signals.indicators import *


logger = get_logger()

@logger.catch
async def fetch_market_data(ticker):
    try:
        async with httpx.AsyncClient() as client:
            # Asynchronously get market data for a ticker
            response = await client.get(tiingo_base_url + f'/iex/?tickers={ticker}&token={tiingo_api_key}')
            response.raise_for_status()
            market_data = response.json()

            return ticker, market_data

    except Exception as e:
        # Handle exceptions appropriately
        logger.error(f"Error processing market data for {ticker}: {e}")
        return ticker, None

def generate_signal(ticker_data):
    ticker, market_data = ticker_data[0], ticker_data[1][0]
    indicators = Indicators()
    if market_data:
        logger.info(f"Generating signal for {ticker}")
        return indicators.macd(ticker=ticker)
    else:
        pass
        # logger.warning(f"Market data for {ticker} is None. Signal generation skipped.")
    

def generate_signal_parallel(ticker_data):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_ticker = {executor.submit(generate_signal, ticker): ticker[1] for ticker in ticker_data}
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                print(result)
                print(f"Signal generated for {ticker}: {result}")
            except Exception as e:
                print(f"Error generating signal for {ticker}: {e}")
        # add code to only call it if there isn't an existing process later

async def main():
    # List of tickers
    tickers = condensed_secmaster_ticker_list
    tickers = secmaster_ticker_list

    # Use asyncio.gather to run fetch_market_data tasks concurrently
    tasks = [fetch_market_data(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks)
    print(results[0])
    # Use ProcessPoolExecutor for parallel signal generation
    # generate_signal_parallel(results)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
