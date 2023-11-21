from alpaca.trading.client import TradingClient
from api_secrets import alpaca_api_key_id, alpaca_api_secret

trading_client = TradingClient(alpaca_api_key_id, alpaca_api_secret)
