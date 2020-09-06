from engines.base import Base
import datetime


class Engine(Base):
    name        = "itbit_btc_usd"
    description = "ItBit"
    uri         = "https://api.itbit.com/v1/markets/XBTUSD/ticker"
    convert     = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['lastPrice'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
