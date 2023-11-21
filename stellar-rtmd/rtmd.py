from api_secrets import alpaca_api_key_id, alpaca_api_secret
from alpaca.data.live.stock import StockDataStream
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

market_data_stream = StockDataStream(api_key=alpaca_api_key_id, secret_key=alpaca_api_secret)

# async handler
async def quote_data_handler(data):
    # quote data will arrive here
    print(data)

market_data_stream.subscribe_quotes(quote_data_handler, "AAPL")

market_data_stream.run()