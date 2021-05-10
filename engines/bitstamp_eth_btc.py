from engines.base import Base
import datetime


class Engine(Base):
    name        = "bitstamp_eth_btc"
    description = "Bitstamp"
    uri         = "https://www.bitstamp.net/api/v2/ticker/ethbtc/"
    convert     = "ETH_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['timestamp']))

        return d_price_info
