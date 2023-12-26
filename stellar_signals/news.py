from resources.api_secrets import alpaca_api_key_id, alpaca_api_secret
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

news_client = NewsClient(alpaca_api_key_id, alpaca_api_secret)


def get_news_for_stock(ticker):
    res = news_client.get_news(request_params=NewsRequest(symbols=ticker))

    return res.json()

get_news_for_stock('AAPL')