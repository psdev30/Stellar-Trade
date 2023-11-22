import time
from api_secrets import alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest
from common.token_bucket import TokenBucket
from ticker_universe import secmaster_ticker_list
import concurrent.futures
from logger_setup import get_logger

logger = get_logger()

stock_data_client = StockHistoricalDataClient(alpaca_api_key_id, alpaca_api_secret, raw_data=True)

@logger.catch
def get_stock_snapshot(symbol, token_bucket):
    while True:
        try:
            # Attempt to consume one token from the bucket
            if token_bucket.consume(1):
                # API call
                res = stock_data_client.get_stock_snapshot(request_params=StockSnapshotRequest(symbol_or_symbols=symbol))
                token_bucket.refill()
                return res  # res is a plain Python dict
            else:
                # If the token bucket is empty, we'll wait for a blink and retry
                print('snapshot: ', token_bucket.tokens)
                time.sleep(0.1)  # Adjust the sleep duration as needed
        except Exception as e:
            print(e)
            # logger.exception('Something went wrong with the token bucket: ', e)
            # If there's an error, wait and retry
            time.sleep(0.1)  # Adjust the sleep duration as needed

@logger.catch
def main():
    token_bucket = TokenBucket(capacity=200, refill_rate=200/60)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for processing all signals for each ticker
        all_signals_futures = [executor.submit(get_stock_snapshot, ticker, token_bucket) for ticker in secmaster_ticker_list]

        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(all_signals_futures):
            try:
                result = future.result()
                print(result)
                print('main: ', token_bucket.tokens)
            except Exception as e:
                print(f"Error processing ticker: {e}")

start_time = time.time()
main()
end_time = time.time()
print(end_time - start_time)