from engines.base import Base
import datetime


class Engine(Base):
    name        = "bitfinex_btc_usdt"
    description = "Bitfinex"
    uri         = "https://api-pub.bitfinex.com/v2/ticker/tBTCUST"
    convert     = "BTC_USDT"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
