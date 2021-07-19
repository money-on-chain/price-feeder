from engines.base import Base
import datetime


class Engine(Base):
    name = "coinbase_btc_usdt"
    description = "Coinbase"
    uri = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
    convert = "BTC_USDT"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['rates']['USDT'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
