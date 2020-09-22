from engines.base import Base
import datetime


class Engine(Base):
    name        = "bitfinex_rif_btc"
    description = "Bitfinex RIF"
    uri         = "https://api-pub.bitfinex.com/v2/ticker/tRIFBTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
