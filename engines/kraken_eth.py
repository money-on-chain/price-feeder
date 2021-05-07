from engines.base import Base
import datetime


class Engine(Base):
    name        = "kraken_eth_usd"
    description = "Kraken"
    uri         = "https://api.kraken.com/0/public/Ticker?pair=ETHUSDT"
    convert     = "ETH_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['ETHUSDT']['c'][0])
        d_price_info['volume'] = float(response_json['result']['ETHUSDT']['v'][1])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
