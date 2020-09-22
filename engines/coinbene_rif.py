from engines.base import Base
import datetime


class Engine(Base):
    name        = "coinbene_rif_btc"
    description = "coinbene RIF"
    uri         = "http://api.coinbene.com/v1/market/ticker?symbol=RIFBTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['ticker'][0]['last'])
        d_price_info['volume'] = float(response_json['ticker'][0]['24hrVol'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
