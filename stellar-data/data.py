from api_secrets import alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest

stock_data_client = StockHistoricalDataClient(alpaca_api_key_id, alpaca_api_secret)


def get_stock_snapshots(symbol):
    res = stock_data_client.get_stock_snapshot(request_params=StockSnapshotRequest(symbol_or_symbols=symbol))
    print(res, type(res)) # res is a plain Python dict

get_stock_snapshots('AAPL')

