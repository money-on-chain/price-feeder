from engines.base import Base
import datetime


class Engine(Base):
    name        = "bithumbpro_rif_btc"
    description = "BitHumb RIF"
    uri         = "https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=RIF-BTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data'][0]['c'])
        d_price_info['volume'] = float(response_json['data'][0]['v'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
