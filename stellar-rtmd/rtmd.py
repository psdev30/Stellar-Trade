import asyncio
import websockets
import simplejson as json
import time
from api_secrets import tiingo_websocket_feed, tiingo_base_url, tiingo_api_key
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest
from resources.ticker_universe_condensed import condensed_secmaster_ticker_list
from logger_setup import get_logger

logger = get_logger()

headers = {
    'api-key': tiingo_api_key,
    'session': 'True'
}

async def subscribe_to_tiingo_feed(uri, subscribe_payload):
    async with websockets.connect(uri) as socket:
        # Send the subscription payload
        await socket.send(json.dumps(subscribe_payload))

        # Continuously receive and process messages
        while True:
            message = await socket.recv()
            process_tiingo_message(message)

def process_tiingo_message(message):
    # Define your logic to process Tiingo messages here
    print(f"Received Tiingo message: {message}")


tiingo_websocket_feed = "wss://api.tiingo.com/iex" 
subscribe_payload = {"eventName": "subscribe", "eventData": {"thresholdLevel": 5, "tickers": condensed_secmaster_ticker_list}}

asyncio.run(subscribe_to_tiingo_feed(tiingo_websocket_feed, subscribe_payload))
