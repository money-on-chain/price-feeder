from engines.base import Base
import datetime


class Engine(Base):
    name        = "rsk_two_rif_btc"
    description = "RSK two RIF"
    uri         = "http://64.225.31.252:3000"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['price'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
