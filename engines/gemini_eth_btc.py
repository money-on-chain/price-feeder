from engines.base import Base
import datetime


class Engine(Base):
    name        = "gemini_eth_btc"
    description = "Gemini"
    uri         = "https://api.gemini.com/v1/pubticker/ethbtc"
    convert     = "ETH_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume']['BTC'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
