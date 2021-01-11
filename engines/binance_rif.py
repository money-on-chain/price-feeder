from engines.base import Base
import datetime


class Engine(Base):
    name        = "binance_rif_btc"
    description = "Binance RIF"
    uri         = "https://api.binance.com/api/v3/ticker/24hr?symbol=RIFBTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['lastPrice'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
