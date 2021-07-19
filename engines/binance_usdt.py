from engines.base import Base
import datetime


class Engine(Base):
    name        = "binance_btc_usdt"
    description = "Binance"
    uri         = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    convert     = "BTC_USDT"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['lastPrice'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info
