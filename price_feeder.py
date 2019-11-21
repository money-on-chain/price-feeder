import os
from optparse import OptionParser
import datetime
import json
import requests
from statistics import median, mean
from pprint import pformat
from timeloop import Timeloop
from web3 import Web3
import boto3
import time

# local imports
from node_manager import NodeManager
from price_engines import price_engine_bitstamp_btc_usd, \
    price_engine_coinbase_btc_usd, \
    price_engine_bitgo_btc_usd, \
    price_engine_bitfinex_btc_usd, price_engine_blockchain_btc_usd, \
    price_engine_binance_btc_usd, price_engine_kucoin_btc_usd, \
    price_engine_kraken_btc_usd, price_engine_bittrex_btc_usd, \
    price_engine_bitfinex_rif_btc, price_engine_bithumbpro_rif_btc

import logging
import logging.config


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/price_feeder.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

log = logging.getLogger('default')


class PricesBase(object):
    def __init__(self, price_options):
        self.options = price_options

    def get_prices(self):
        l_prices = list()
        d_info = dict()

        return l_prices, d_info

    def get_median(self):
        """ Median """

        prices = self.get_prices()
        return median(prices)

    def get_mean(self):
        """ Median """

        prices = self.get_prices()
        return mean(prices)

    def get_ponderated(self):
        """ Ponderated """

        return

    def price(self):
        """ Ponderated """

        self.get_ponderated()


class PricesBtcUsd(PricesBase):

    def get_prices(self):

        # create persistent HTTP connection
        session = requests.Session()
        l_prices = list()
        d_info = dict()

        price_fetchers = self.options['price_fetchers']
        min_volume = self.options['min_volume']
        timeout_request = self.options['timeout_request']

        # coinbase
        if 'coinbase' in price_fetchers:
            price_info, price_err = price_engine_coinbase_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['coinbase'] = d_pricer

        # bitstamp
        if 'bitstamp' in price_fetchers:
            price_info, price_err = price_engine_bitstamp_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitstamp'] = d_pricer

        # bitgo
        if 'bitgo' in price_fetchers:
            price_info, price_err = price_engine_bitgo_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitgo'] = d_pricer

        # bitfinex
        if 'bitfinex' in price_fetchers:
            price_info, price_err = price_engine_bitfinex_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitfinex'] = d_pricer

        # blockchain
        if 'blockchain' in price_fetchers:
            price_info, price_err = price_engine_blockchain_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['blockchain'] = d_pricer

        # bittrex
        if 'bittrex' in price_fetchers:
            price_info, price_err = price_engine_bittrex_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bittrex'] = d_pricer

        # kraken
        if 'kraken' in price_fetchers:
            price_info, price_err = price_engine_kraken_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['kraken'] = d_pricer

        # kucoin
        if 'kucoin' in price_fetchers:
            price_info, price_err = price_engine_kucoin_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['kucoin'] = d_pricer

        # binance
        if 'binance' in price_fetchers:
            price_info, price_err = price_engine_binance_btc_usd(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['binance'] = d_pricer

        return l_prices, d_info

    def get_ponderated(self):
        """ Ponderated """

        price_ponderations = self.options['price_ponderations']
        price_fetchers = self.options['price_fetchers']

        if len(price_ponderations) != len(price_fetchers):
            raise Exception("Error! Price ponderations and price feeder list not equal!")

        prices_list, prices_dict = self.get_prices()

        l_ponderated = list()
        d_ponderated = dict()
        missing_portions = 0.0

        if len(prices_list) != len(price_ponderations):
            for index, price_name in enumerate(price_fetchers):
                if price_name not in prices_dict:
                    missing_portions += price_ponderations[index]
                    continue

        if not prices_list:
            raise Exception("No price values from API. check connection or all down?.")

        eq_missing_portions = missing_portions / len(prices_list)

        for index, price_name in enumerate(price_fetchers):
            if price_name not in prices_dict:
                continue

            portion = price_ponderations[index] + eq_missing_portions
            p_ponderated = prices_dict[price_name]['price'] * portion
            l_ponderated.append(p_ponderated)

            d_info = dict()
            d_info['price'] = format(prices_dict[price_name]['price'], '.2f')
            d_info['portion'] = portion
            d_info['ponderated'] = format(p_ponderated, '.2f')
            d_ponderated[price_name] = d_info

        log.debug(pformat(d_ponderated))

        return sum(l_ponderated)

    def price(self):
        """ Ponderated """

        return self.get_ponderated()


class PricesRifUsd(PricesBtcUsd):

    def get_prices_rif(self):
        # create persistent HTTP connection
        session = requests.Session()
        l_prices = list()
        d_info = dict()

        price_fetchers = self.options['price_rif_fetchers']
        min_volume = self.options['min_volume']
        timeout_request = self.options['timeout_request']

        # bitfinex
        if 'bitfinex' in price_fetchers:
            price_info, price_err = price_engine_bitfinex_rif_btc(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitfinex'] = d_pricer

        # bithumbpro
        if 'bithumbpro' in price_fetchers:
            price_info, price_err = price_engine_bithumbpro_rif_btc(session, log, timeout=timeout_request)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bithumbpro'] = d_pricer

        return l_prices, d_info

    def get_rif_ponderated(self):

        price_ponderations = self.options['price_rif_ponderations']
        price_fetchers = self.options['price_rif_fetchers']

        if len(price_ponderations) != len(price_fetchers):
            raise Exception("Error! Price ponderations and price feeder list not equal!")

        prices_list, prices_dict = self.get_prices_rif()

        l_ponderated = list()
        d_ponderated = dict()
        missing_portions = 0.0

        if len(prices_list) != len(price_ponderations):
            for index, price_name in enumerate(price_fetchers):
                if price_name not in prices_dict:
                    missing_portions += price_ponderations[index]
                    continue

        eq_missing_portions = missing_portions / len(prices_list)

        for index, price_name in enumerate(price_fetchers):
            if price_name not in prices_dict:
                continue

            portion = price_ponderations[index] + eq_missing_portions
            p_ponderated = prices_dict[price_name]['price'] * portion
            l_ponderated.append(p_ponderated)

            d_info = dict()
            d_info['price'] = format(prices_dict[price_name]['price'], '.18f')
            d_info['portion'] = portion
            d_info['ponderated'] = format(p_ponderated, '.18f')
            d_ponderated[price_name] = d_info

        log.info(pformat(d_ponderated))

        return sum(l_ponderated)

    def price(self):
        """ Ponderated """

        btc_usd_price_ponderated = self.get_ponderated()
        btc_rif_price_ponderated = self.get_rif_ponderated()

        usd_rif_price = btc_rif_price_ponderated * btc_usd_price_ponderated

        return usd_rif_price


class ContractManager:
    MoCMedianizer = None
    PriceFeed = None


class PriceFeeder:

    tl = Timeloop()
    last_price = 0.0

    def __init__(self, path_to_config, network_nm, build_dir_nm):

        config_options = self.options_from_config(path_to_config)
        config_options['build_dir'] = build_dir_nm
        self.options = config_options

        self.nm = NodeManager(options=config_options, network=network_nm)

        self.cm = ContractManager()

        if self.options['app_mode'] == 'MoC':
            self.price_source = PricesBtcUsd(self.options)
        elif self.options['app_mode'] == 'rrc20':
            self.price_source = PricesRifUsd(self.options)
        else:
            raise Exception("Error! Config app_mode not recognize!")

    @staticmethod
    def options_from_config(filename='config.json'):
        """ Options from file config.json """

        with open(filename) as f:
            config_options = json.load(f)

        return config_options

    @staticmethod
    def aws_put_metric_heart_beat(value):
        # Create CloudWatch client
        cloudwatch = boto3.client('cloudwatch')

        # Put custom metrics
        cloudwatch.put_metric_data(
            MetricData=[
                {
                    'MetricName': os.environ['PRICE_FEEDER_NAME'],
                    'Dimensions': [
                        {
                            'Name': 'PriceFeeder',
                            'Value': 'Status'
                        },
                    ],
                    'Unit': 'None',
                    'Value': value
                },
            ],
            Namespace='MOC/PRICE_FEEDER'
        )

    def connect(self):
        self.nm.connect_node()
        self.load_contracts()

    def load_contracts(self):

        path_build = self.options['build_dir']
        address_price_feed = self.options['networks'][network]['addresses']['PriceFeed']

        self.cm.PriceFeed = self.nm.load_json_contract(os.path.join(path_build, "PriceFeed.json"),
                                                       deploy_address=address_price_feed)

    def post_price(self, p_price):

        address_moc_medianizer = Web3.toChecksumAddress(self.options['networks'][network]['addresses']['MoCMedianizer'])

        delay = self.options['block_expiration']
        last_block = self.nm.get_block('latest')
        expiration = last_block.timestamp + delay
        try:
            tx_hash = self.nm.fnx_transaction(self.cm.PriceFeed, 'post',
                                              int(p_price),
                                              int(expiration),
                                              address_moc_medianizer)
            tx_receipt = self.nm.wait_transaction_receipt(tx_hash)

        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_heart_beat(0)
        else:
            log.debug(tx_receipt)
            log.info("SUCCESS!. Price Set: [{0}]".format(p_price))
            self.aws_put_metric_heart_beat(1)

    def price_setter(self):

        last_price = self.last_price
        price_variation_accepted = self.options['price_variation_accepted'] * last_price
        min_price = abs(last_price - price_variation_accepted)
        max_price = last_price + price_variation_accepted

        price_medianizer = self.price_source.price()

        price_to_set = price_medianizer * 10 ** 18
        log.debug("Last price: [{0}] Min: [{1}] Max: [{2}] New price: [{3}]".format(last_price,
                                                                                    min_price,
                                                                                    max_price,
                                                                                    price_medianizer))
        if price_medianizer < min_price or price_medianizer > max_price:
            self.post_price(price_to_set)
        else:
            log.info("WARNING! NOT SETTING is the same to last +- variation! [{0}]".format(price_medianizer))
            self.aws_put_metric_heart_beat(1)
        
        self.last_price = price_medianizer

        return price_medianizer

    def job_ponderated_price(self):

        ponderated = self.price_source.get_ponderated()
        print(ponderated)

    def job_price_setter(self):

        try:
            self.connect()
            last_price = self.price_setter()
        except Exception as e:
            log.error(e, exc_info=True)

    def add_jobs(self):

        self.tl._add_job(self.job_price_setter, datetime.timedelta(seconds=self.options['interval']))

    def time_loop_start(self):

        self.add_jobs()
        #self.tl.start(block=True)
        self.tl.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.tl.stop()
                break


if __name__ == '__main__':

    usage = '%prog [options] '
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--network', action='store', dest='network', type="string", help='network')

    parser.add_option('-c', '--config', action='store', dest='config', type="string", help='config')

    parser.add_option('-b', '--build', action='store', dest='build', type="string", help='build')

    (options, args) = parser.parse_args()

    if not options.config:
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    else:
        config_path = options.config

    if not options.network:
        network = 'local'
    else:
        network = options.network

    if not options.build:
        build_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build')
    else:
        build_dir = options.build

    price_feeder = PriceFeeder(config_path, network, build_dir)
    price_feeder.time_loop_start()
