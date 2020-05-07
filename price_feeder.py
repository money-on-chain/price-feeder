"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
    software and other kinds of works.

  Martin Mulone @2020 Moneyonchain
"""


import os
from optparse import OptionParser
import datetime
import json
from timeloop import Timeloop
from web3 import Web3
import boto3
import time
import decimal
from moneyonchain.manager import ConnectionManager
from moneyonchain.moc import MoCMedianizer, PriceFeed
from moneyonchain.rdoc import RDOCMoCMedianizer, RDOCPriceFeed

# local imports
from price_engines import PriceEngines

import logging
import logging.config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger('default')


class PriceFeederJob:

    def __init__(self, price_f_config, network_nm):

        self.options = price_f_config
        self.network = network_nm
        self.connection_manager = ConnectionManager(options=self.options, network=self.network)
        self.app_mode = self.options['networks'][network]['app_mode']

        if self.app_mode == 'RIF':
            self.contract_medianizer = RDOCMoCMedianizer(self.connection_manager)
            self.contract_price_feed = RDOCPriceFeed(self.connection_manager)

            address_contract_moc_medianizer = Web3.toChecksumAddress(
                self.options['networks'][network]['addresses']['RIF_source_price_btc'])
            self.contract_moc_medianizer = RDOCMoCMedianizer(self.connection_manager,
                                                             contract_address=address_contract_moc_medianizer)
        elif self.app_mode == 'MoC':
            self.contract_medianizer = MoCMedianizer(self.connection_manager)
            self.contract_price_feed = PriceFeed(self.connection_manager)
        else:
            raise Exception("Not valid APP Mode")

        self.tl = Timeloop()
        self.last_price = 0.0

        self.price_source = PriceEngines(self.options['networks'][self.network]['price_engines'],
                                         log=log,
                                         app_mode=self.app_mode)

    @staticmethod
    def aws_put_metric_exception(value):

        if 'AWS_ACCESS_KEY_ID' not in os.environ:
            return

        # Create CloudWatch client
        cloudwatch = boto3.client('cloudwatch')

        # Put custom metrics
        cloudwatch.put_metric_data(
            MetricData=[
                {
                    'MetricName': os.environ['PRICE_FEEDER_NAME'],
                    'Dimensions': [
                        {
                            'Name': 'PRICEFEEDER',
                            'Value': 'Error'
                        },
                    ],
                    'Unit': 'None',
                    'Value': value
                },
            ],
            Namespace='MOC/EXCEPTIONS'
        )

    def get_price_btc(self):

        return decimal.Decimal(self.price_source.prices_weighted_median())

    def get_price_rif(self):

        btc_usd_price = self.contract_moc_medianizer.price()
        btc_rif_price = decimal.Decimal(self.price_source.prices_weighted_median())

        usd_rif_price = btc_rif_price * btc_usd_price

        return usd_rif_price

    def price_feed(self):

        last_price = decimal.Decimal(self.last_price)
        price_variation_accepted = decimal.Decimal(
            self.options['networks'][self.network]['price_variation_write_blockchain']) * last_price
        min_price = abs(last_price - price_variation_accepted)
        max_price = last_price + price_variation_accepted

        if self.options['networks'][self.network]['app_mode'] == 'MoC':
            price_no_precision = self.get_price_btc()
        elif self.options['networks'][self.network]['app_mode'] == 'RIF':
            price_no_precision = self.get_price_rif()
        else:
            raise Exception("Error! Config app_mode not recognize!")

        price_to_set = price_no_precision * 10 ** 18
        log.debug("Last price: [{0}] Min: [{1}] Max: [{2}] New price: [{3}]".format(
            last_price,
            min_price,
            max_price,
            price_no_precision))
        if price_no_precision < min_price or price_no_precision > max_price:
            self.contract_price_feed.post(price_to_set)
        else:
            log.info("NOT SETTING is the same to last +- variation! [{0}]".format(
                price_no_precision))

        self.last_price = price_no_precision

        return price_no_precision

    def job_price_feed(self):

        try:
            self.price_feed()
        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_exception(1)

    def add_jobs(self):

        # creating the alarm
        self.aws_put_metric_exception(0)

        # adding the jobs
        self.tl._add_job(self.job_price_feed, datetime.timedelta(
            seconds=self.options['interval']))

    def time_loop_start(self):

        self.add_jobs()
        self.tl.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.tl.stop()
                break


def options_from_config(filename='config.json'):
    """ Options from file config.json """

    with open(filename) as f:
        config_options = json.load(f)

    return config_options


if __name__ == '__main__':

    usage = '%prog [options] '
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--network', action='store', dest='network', type="string", help='network')

    parser.add_option('-c', '--config', action='store', dest='config', type="string", help='config')

    (options, args) = parser.parse_args()

    if 'PRICE_FEEDER_CONFIG' in os.environ:
        config = json.loads(os.environ['PRICE_FEEDER_CONFIG'])
    else:
        if not options.config:
            config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
        else:
            config_path = options.config

        config = options_from_config(config_path)

    if 'PRICE_FEEDER_NETWORK' in os.environ:
        network = os.environ['PRICE_FEEDER_NETWORK']
    else:
        if not options.network:
            network = 'rdocTestnet'
        else:
            network = options.network

    price_feeder = PriceFeederJob(config, network)
    price_feeder.time_loop_start()
