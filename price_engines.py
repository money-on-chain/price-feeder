import requests
import datetime
from statistics import median, mean
import numpy as np
from pprint import pformat


def weighted_median(values, weights):
    ''' compute the weighted median of values list. The
weighted median is computed as follows:
    1- sort both lists (values and weights) based on values.
    2- select the 0.5 point from the weights and return the corresponding values as results
    e.g. values = [1, 3, 0] and weights=[0.1, 0.3, 0.6] assuming weights are probabilities.
    sorted values = [0, 1, 3] and corresponding sorted weights = [0.6,     0.1, 0.3] the 0.5 point on
    weight corresponds to the first item which is 0. so the weighted     median is 0.'''

    # convert the weights into probabilities
    sum_weights = sum(weights)
    weights = np.array([(w*1.0)/sum_weights for w in weights])
    # sort values and weights based on values
    values = np.array(values)
    sorted_indices = np.argsort(values)
    values_sorted  = values[sorted_indices]
    weights_sorted = weights[sorted_indices]
    # select the median point
    it = np.nditer(weights_sorted, flags=['f_index'])
    accumulative_probability = 0
    median_index = -1
    while not it.finished:
        accumulative_probability += it[0]
        if accumulative_probability > 0.5:
            median_index = it.index
            return values_sorted[median_index]
        elif accumulative_probability == 0.5:
            median_index = it.index
            it.iternext()
            next_median_index = it.index
            return np.mean(values_sorted[[median_index, next_median_index]])
        it.iternext()

    return values_sorted[median_index]


class PriceEngineBase(object):
    name = "base_engine"
    description = "Base Engine"
    uri = "http://api.pricefetcher.com/BTCUSD"
    convert = "BTC_USD"

    def __init__(self, log, timeout=10, uri=None):
        self.log = log
        self.timeout = timeout
        if uri:
            self.uri = uri

    def send_alarm(self, message, level=0):
        self.log.error(message)

    def fetch(self, session):

        try:
            response = session.get(self.uri, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            err_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(self.name, http_err)
            self.send_alarm(err_msg)
            return None, err_msg
        except Exception as err:
            err_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(self.name, err)
            self.send_alarm(err_msg)
            return None, err_msg

        if not response:
            err_msg = "Error! No response from server on get price. Engine: {0}".format(self.name)
            self.send_alarm(err_msg)
            return None, err_msg

        if response.status_code != 200:
            err_msg = "Error! Error response from server on get price. Engine: {0}".format(self.name)
            self.send_alarm(err_msg)
            return None, err_msg

        return response, ""

    @staticmethod
    def map(response_json):

        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['timestamp']))

        return d_price_info

    def get_price(self, session):

        r, err_msg = self.fetch(session)
        if not r:
            return None, err_msg

        try:
            response_json = r.json()
            d_price_info = self.map(response_json)
        except Exception as err:
            err_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(self.name, err)
            self.send_alarm(err_msg)
            return None, err_msg

        return d_price_info, None


class BitstampBTCUSD(PriceEngineBase):
    name = "bitstamp_btc_usd"
    description = "Bitstamp"
    uri = "https://www.bitstamp.net/api/v2/ticker/btcusd/"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['timestamp']))

        return d_price_info


class CoinBaseBTCUSD(PriceEngineBase):
    name = "coinbase_btc_usd"
    description = "Coinbase"
    #uri = "https://api.coinbase.com/v2/prices/BTC-USD/buy"
    uri = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['amount'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BitGOBTCUSD(PriceEngineBase):
    name = "bitgo_btc_usd"
    description = "BitGO"
    uri = "https://www.bitgo.com/api/v1/market/latest"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['latest']['currencies']['USD']['last'])
        d_price_info['volume'] = float(response_json['latest']['currencies']['USD']['total_vol'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(
            int(response_json['latest']['currencies']['USD']['timestamp']))

        return d_price_info


class BitfinexBTCUSD(PriceEngineBase):
    name = "bitfinex_btc_usd"
    description = "Bitfinex"
    uri = "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BlockchainBTCUSD(PriceEngineBase):
    name = "blockchain_btc_usd"
    description = "Blockchain"
    uri = "https://blockchain.info/ticker"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['USD']['last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BinanceBTCUSD(PriceEngineBase):
    name = "binance_btc_usd"
    description = "Binance"
    uri = "https://api.binance.com/api/v1/ticker/24hr?symbol=BTCUSDT"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['lastPrice'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class KucoinBTCUSD(PriceEngineBase):
    name = "kucoin_btc_usd"
    description = "Binance"
    uri = "https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['last'])
        d_price_info['volume'] = float(response_json['data']['vol'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class KrakenBTCUSD(PriceEngineBase):
    name = "kraken_btc_usd"
    description = "Kraken"
    uri = "https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['XXBTZUSD']['c'][0])
        d_price_info['volume'] = float(response_json['result']['XXBTZUSD']['v'][1])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BittrexBTCUSD(PriceEngineBase):
    name = "bittrex_btc_usd"
    description = "Bittrex"
    uri = "https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC"
    convert = "BTC_USD"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['Last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BitfinexRIFBTC(PriceEngineBase):
    name = "bitfinex_rif_btc"
    description = "Bitfinex RIF"
    uri = "https://api-pub.bitfinex.com/v2/ticker/tRIFBTC"
    convert = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


class BithumbproRIFBTC(PriceEngineBase):
    name = "bithumbpro_rif_btc"
    description = "BitHumb RIF"
    uri = "https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=RIF-BTC"
    convert = "RIF_BTC"

    @staticmethod
    def map(response_json):
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data'][0]['c'])
        d_price_info['volume'] = float(response_json['data'][0]['v'])
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info


base_engines_names = {
    "coinbase": CoinBaseBTCUSD,
    "bitstamp": BitstampBTCUSD,
    "bitgo": BitGOBTCUSD,
    "bitfinex": BitfinexBTCUSD,
    "blockchain": BlockchainBTCUSD,
    "bittrex": BittrexBTCUSD,
    "kraken": KrakenBTCUSD,
    "kucoin": KucoinBTCUSD,
    "binance": BinanceBTCUSD,
    "bitfinex_rif": BitfinexRIFBTC,
    "bithumbpro_rif": BithumbproRIFBTC
}


class LogMeta(object):

    @staticmethod
    def info(msg):
        print("INFO: {0}".format(msg))

    @staticmethod
    def error(msg):
        print("ERROR: {0}".format(msg))


class PriceEngines(object):

    def __init__(self, price_options, log=None, engines_names=None):
        self.price_options = price_options
        self.engines = list()

        # log settings
        if not log:
            log = LogMeta()
        self.log = log

        # engine names
        if not engines_names:
            engines_names = base_engines_names

        self.engines_names = engines_names

        self.add_engines()

    def add_engines(self):

        price_engines = self.price_options
        for price_engine in price_engines:
            engine_name = price_engine["name"]

            if engine_name not in self.engines_names:
                raise Exception("The engine price name not in the avalaible list")

            engine = self.engines_names.get(engine_name)
            i_engine = engine(self.log)

            d_engine = dict()
            d_engine["engine"] = i_engine
            d_engine["ponderation"] = price_engine["ponderation"]
            d_engine["min_volume"] = price_engine["min_volume"]
            d_engine["max_delay"] = price_engine["max_delay"]
            d_engine["name"] = engine_name
            self.engines.append(d_engine)

    def fetch_prices(self, session=None):

        # create persistent HTTP connection
        if not session:
            session = requests.Session()

        prices = list()
        for engine in self.engines:
            d_price, err_msg = engine["engine"].get_price(session)
            if d_price:
                i_price = dict()
                i_price['name'] = engine["name"]
                i_price['ponderation'] = engine["ponderation"]
                i_price['price'] = d_price["price"]
                i_price['volume'] = d_price["volume"]
                i_price['timestamp'] = d_price["timestamp"]
                i_price['min_volume'] = engine["min_volume"]
                i_price['max_delay'] = engine["max_delay"]

                if i_price["min_volume"] > 0:
                    # the evalution of volume is on
                    if not i_price['volume'] > i_price["min_volume"]:
                        # is not added to the price list
                        self.log.warning("Not added to the list because is not at to the desire volume: %s" %
                                         i_price['name'])
                        continue

                prices.append(i_price)

        return prices

    def get_mean(self, session=None):

        f_prices = self.fetch_prices(session=session)
        prices = list()
        for f_price in f_prices:
            price = f_price["price"]
            prices.append(price)

        return mean(prices)

    def get_weighted(self, session=None):

        f_prices = self.fetch_prices(session=session)

        missing_portions = 0.0

        if len(f_prices) < 3:
            raise Exception("At least we need 3 price sources.")

        if len(f_prices) != len(self.engines):

            l_fetched = list()
            for pr in f_prices:
                l_fetched.append(pr['name'])

            # we have to recalculate the ponderation, some price is missing
            for d_engine in self.engines:
                if d_engine["name"] not in l_fetched:
                    missing_portions += d_engine["ponderation"]

        eq_missing_portions = missing_portions / len(f_prices)

        for pr in f_prices:
            portion = pr["ponderation"] + eq_missing_portions
            pr["price_ponderation"] = portion
            pr["price_ponderated"] = pr["price"] * portion

        self.log.info(f_prices)
        self.log.info(pformat(f_prices))

        return f_prices

    @staticmethod
    def get_weighted_median(fetch_weighted_prices):

        l_prices = list()
        l_weights = list()

        for p_price in fetch_weighted_prices:
            l_prices.append(p_price['price'])
            l_weights.append(p_price['price_ponderation'])

        w_median = weighted_median(l_prices, l_weights)
        return w_median

    def prices_weighted_median(self):

        w_prices = self.get_weighted()
        w_median = self.get_weighted_median(w_prices)
        return w_median

