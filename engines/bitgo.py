from engines.base import Base
import datetime


class Engine(Base):
    name        = "bitgo_btc_usd"
    description = "BitGO"
    uri         = "https://www.bitgo.com/api/v1/market/latest"
    convert     = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['latest']['currencies']['USD']['last'])
        d_price_info['volume'] = float(response_json['latest']['currencies']['USD']['total_vol'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(
            int(response_json['latest']['currencies']['USD']['timestamp']))

        return d_price_info
