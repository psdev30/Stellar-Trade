from alpaca.trading.client import TradingClient
from api_secrets import alpaca_api_key_id, alpaca_api_secret
from logger_setup import get_logger

logger = get_logger()

trading_client = TradingClient(alpaca_api_key_id, alpaca_api_secret)
