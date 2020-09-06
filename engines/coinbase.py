from engines.base import Base
import datetime


class Engine(Base):
    name = "coinbase_btc_usd"
    description = "Coinbase"
    uri = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['amount'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
