from engines.base import Base
import datetime


class Engine(Base):
    name        = "bittrex_eth_usd"
    description = "Bittrex"
    uri         = "https://api.bittrex.com/api/v1.1/public/getticker?market=USD-ETH"
    convert     = "ETH_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['Last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
