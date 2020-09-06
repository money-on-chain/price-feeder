from engines.base import Base
import datetime


class Engine(Base):
    name        = "okcoin_btc_usd"
    description = "OkCoin"
    uri         = "https://www.okcoin.com/api/spot/v3/instruments/BTC-USD/ticker"
    convert     = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
