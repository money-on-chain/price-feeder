from engines.base import Base
import datetime


class Engine(Base):
    name        = "coinbene_rif_btc"
    description = "coinbene RIF"
    uri         = "https://openapi-exchange.coinbene.com/api/exchange/v2/market/ticker/one?symbol=RIF%2FBTC"
    convert     = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['latestPrice'])
        d_price_info['volume'] = float(response_json['data']['volume24h'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
