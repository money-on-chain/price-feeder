from engines.base import Base
import datetime


class Engine(Base):
    name        = "kucoin_btc_usd"
    description = "Binance"
    uri         = "https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT"
    convert     = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['last'])
        d_price_info['volume'] = float(response_json['data']['vol'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
