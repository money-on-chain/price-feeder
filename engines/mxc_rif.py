from engines.base import Base
import datetime


class Engine(Base):
    name        = "mxc_rif_btc"
    description = "MXC RIF"
    uri         = "https://www.mxc.com/open/api/v2/market/ticker?symbol=RIF_BTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price']     = float(response_json['data'][0]['last'])
        d_price_info['volume']    = float(response_json['data'][0]['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
