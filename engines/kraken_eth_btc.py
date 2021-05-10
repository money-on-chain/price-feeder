from engines.base import Base
import datetime


class Engine(Base):
    name        = "kraken_eth_btc"
    description = "Kraken"
    uri         = "https://api.kraken.com/0/public/Ticker?pair=ETHBTC"
    convert     = "ETH_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['XETHXXBT']['c'][0])
        d_price_info['volume'] = float(response_json['result']['XETHXXBT']['v'][1])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
