from engines.base import Base
import datetime


class Engine(Base):
    name        = "cex_btc_usd"
    description = "Cex"
    uri         = "https://cex.io/api/ticker/BTC/USD"
    convert     = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
