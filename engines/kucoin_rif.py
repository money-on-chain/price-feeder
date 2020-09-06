from engines.base import Base
import datetime


class Engine(Base):
    name        = "kucoin_rif_btc"
    description = "Kucoin RIF"
    uri         = "https://openapi-v2.kucoin.com/api/v1/market/orderbook/level1?symbol=RIF-BTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['price'])
        d_price_info['volume'] = float(response_json['data']['size'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
