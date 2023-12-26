import time
from resources.api_secrets import *
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from resources.logger_setup import get_logger
import requests as r

logger = get_logger()

headers = {
    'Content-Type': 'application/json'
}

@logger.catch
def fetch_market_data(ticker):
    try:
        response = r.get('https://jsonplaceholder.typicode.com/todos')
        # response = r.get(tiingo_base_url + f'/iex/?tickers={ticker}&token={tiingo_api_key}')
        response.raise_for_status()
        return response.json()

    except Exception as e:
        pass
        # Handle exceptions appropriately
        # logger.error(f"Error processing market data for {ticker}: {e}")


def generateSignal(ticker, datapoint):
    # Your logic to generate a signal using the ticker and market data
    print(f'got to generate signal with: {ticker}')
    # logger.info(f"Generating signal for {ticker}: {datapoint}")
    

def main():
    # List of tickers
    tickers = condensed_secmaster_ticker_list
    # tickers = ['GOOG', 'AAPL', 'Z', 'TSLA', 'NVDA']

    for ticker in tickers:
        data = fetch_market_data(ticker=ticker)
        generateSignal(ticker, data)


if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)