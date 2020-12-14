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
from moneyonchain.moc import MoCMedianizer, PriceFeed, MoCState
from moneyonchain.rdoc import RDOCMoCMedianizer, RDOCPriceFeed, RDOCMoCState

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
        self.app_mode = self.options['networks'][self.network]['app_mode']

        # backup writes
        self.backup_writes = 0

        if self.app_mode == 'RIF':
            self.contract_medianizer = RDOCMoCMedianizer(self.connection_manager)
            self.contract_price_feed = RDOCPriceFeed(self.connection_manager)

            address_contract_moc_medianizer = Web3.toChecksumAddress(
                self.options['networks'][network]['addresses']['RIF_source_price_btc'])
            self.contract_moc_medianizer = RDOCMoCMedianizer(self.connection_manager,
                                                             contract_address=address_contract_moc_medianizer)
            self.contract_moc_state = RDOCMoCState(self.connection_manager)

        elif self.app_mode == 'MoC':
            self.contract_medianizer = MoCMedianizer(self.connection_manager)
            self.contract_price_feed = PriceFeed(self.connection_manager)
            self.contract_moc_state = MoCState(self.connection_manager)
        
        else:
            raise Exception("Not valid APP Mode")

        

        self.tl = Timeloop()
        self.last_price = 0.0
        self.last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=300)

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

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.network]['block_expiration']

        # get the last price we insert as a feeder
        last_price = decimal.Decimal(self.last_price)

        # get the price from oracle
        last_price_oracle = self.contract_medianizer.peek()[0]

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        # get the price source depending on the project
        if self.options['networks'][self.network]['app_mode'] == 'MoC':
            price_no_precision = self.get_price_btc()
        elif self.options['networks'][self.network]['app_mode'] == 'RIF':
            price_no_precision = self.get_price_rif()
        else:
            raise Exception("Error! Config app_mode not recognize!")      

        # if the price is below the floor, I don't publish it
        price_floor = self.options['networks'][self.network].get('price_floor', None)
        if price_floor != None:
            price_floor = str(price_floor)
            ema = self.contract_moc_state.bitcoin_moving_average()
            kargs = {'ema': float(ema)}
            try:
                price_floor = decimal.Decimal(str(eval(price_floor, kargs)))
            except Exception as e:
                raise ValueError('price_floor: {}'.format(e))
        not_under_the_floor = not(price_floor and price_floor>price_no_precision)

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        # is more than 5 minutes from the last write
        is_in_time = (self.last_price_timestamp + datetime.timedelta(seconds=300) < now)

        log.info("[PRICE FEED] ORACLE: [{0:.4f}] MIN: [{1:.4f}] MAX: [{2:.4f}] NEW: [{3:.4f}] IS IN RANGE: [{4}] IS IN TIME: [{5}]".format(
            last_price_oracle,
            min_price,
            max_price,
            price_no_precision,
            is_in_range,
            is_in_time))

        # IF is in range or not in range but is in time
        if not_under_the_floor and (is_in_range or (not is_in_range and is_in_time)):

            # set the precision to price
            price_to_set = price_no_precision * 10 ** 18

            # submit the value to contract
            self.contract_price_feed.post(price_to_set,
                                          block_expiration=block_expiration,
                                          gas_limit=2000000)

            # save the last price to compare
            self.last_price = price_no_precision

            # save the last timestamp to compare
            self.last_price_timestamp = datetime.datetime.now()

        return price_no_precision

    def price_feed_backup(self):
        """ Only start to work only when we dont have price """

        if not self.contract_medianizer.compute()[1] or self.backup_writes > 0:
            self.price_feed()
            self.aws_put_metric_exception(1)

            if self.backup_writes <= 0:
                if 'backup_writes' in self.options:
                    self.backup_writes = self.options['backup_writes']
                else:
                    self.backup_writes = 100

            self.backup_writes -= 1

            log.error("[BACKUP MODE ACTIVATED!] WRITE REMAINING:{0}".format(self.backup_writes))

        else:
            log.info("[NO BACKUP]")

    def job_price_feed(self):

        try:
            self.price_feed()
        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_exception(1)

    def job_price_feed_backup(self):

        try:
            self.price_feed_backup()
        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_exception(1)

    def add_jobs(self):

        # creating the alarm
        self.aws_put_metric_exception(0)

        backup_mode = False
        if 'backup_mode' in self.options:
            if self.options['backup_mode']:
                backup_mode = True

        if backup_mode:
            log.info("Job Price feeder as BACKUP!")
            self.tl._add_job(self.job_price_feed_backup, datetime.timedelta(
                seconds=self.options['interval']))
        else:
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
            config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'enviroments', 'moc-testnet', 'config.json')
        else:
            config_path = options.config

        config = options_from_config(config_path)

    if 'PRICE_FEEDER_NETWORK' in os.environ:
        network = os.environ['PRICE_FEEDER_NETWORK']
    else:
        if not options.network:
            network = 'mocTestnet'
        else:
            network = options.network

    price_feeder = PriceFeederJob(config, network)
    price_feeder.time_loop_start()
