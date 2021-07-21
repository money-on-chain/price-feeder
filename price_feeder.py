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

__VERSION__ = '2.0.7'


import os
from optparse import OptionParser
import datetime
import json
from timeloop import Timeloop
from web3 import Web3
import boto3
import time
import decimal
from moneyonchain.networks import network_manager
from moneyonchain.medianizer import MoCMedianizer, PriceFeed, RDOCMoCMedianizer, RDOCPriceFeed
from moneyonchain.moc import MoCState
from moneyonchain.rdoc import RDOCMoCState

# local imports
from price_engines import PriceEngines

import logging
import logging.config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger('default')
log.info("Starting Price Feeder version {0}".format(__VERSION__))


class PriceFeederJobBase:

    def __init__(self, price_f_config, config_net, connection_net):

        self.options = price_f_config
        self.config_network = config_net
        self.connection_network = connection_net
        self.last_block = 0

        # install custom network if needit
        if self.connection_network.startswith("https") or self.connection_network.startswith("http"):
            a_connection = self.connection_network.split(',')
            host = a_connection[0]
            chain_id = a_connection[1]

            network_manager.add_network(
                network_name='rskCustomNetwork',
                network_host=host,
                network_chainid=chain_id,
                network_explorer='https://blockscout.com/rsk/mainnet/api',
                force=False
            )

            self.connection_network = 'rskCustomNetwork'

            log.info("Using custom network... id: {}".format(self.connection_network))

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']

        self.app_mode = self.options['networks'][self.config_network]['app_mode']

        log.info("Starting with MoCMedianizer: {}".format(address_medianizer))
        log.info("Starting with PriceFeed: {}".format(address_pricefeed))
        log.info("Starting with app_mode: {}".format(self.app_mode))

        # simulation don't write to blockchain
        self.is_simulation = False
        if 'is_simulation' in self.options:
            self.is_simulation = self.options['is_simulation']

        # Min prices source
        self.min_prices_source = 1
        if 'min_prices_source' in self.options:
            self.min_prices_source = self.options['min_prices_source']

        # backup writes
        self.backup_writes = 0

        self.tl = Timeloop()
        self.last_price = 0.0
        self.last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=300)

        self.price_source = PriceEngines(self.options['networks'][self.config_network]['price_engines'],
                                         log=log,
                                         app_mode=self.app_mode,
                                         min_prices=self.min_prices_source)

        self.connect()

    def connect(self):

        # connection network is the brownie connection network
        # config network is our enviroment we want to connect
        network_manager.connect(connection_network=self.connection_network,
                                config_network=self.config_network)

    def init_contracts(self):
        """ Init contracts """
        pass

    @staticmethod
    def aws_put_metric_exception(value):
        """ Only for AWS cloudwatch"""

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

    def price_feed(self):
        """ Post price """
        return

    def price_feed_backup(self):
        """ Post price in backup mode """
        return

    def reconnect_on_lost_chain(self):

        block = network_manager.block_number

        if not self.last_block:
            self.last_block = block
            return

        if block <= self.last_block:
            # this means no new blocks from the last call,
            # so this means a halt node, try to reconnect.

            log.error("[ERROR BLOCKCHAIN CONNECT!] Same block from the last time! going to reconnect!")

            # Raise exception
            self.aws_put_metric_exception(1)

            # first disconnect
            network_manager.disconnect()

            # and then reconnect all again
            self.connect()

            # init contracts again
            self.init_contracts()

        log.info("[RECONNECT] :: Reconnect on lost chain :: OK :: Block height: {1}/{0} ".format(
            block, self.last_block))

        # save the last block
        self.last_block = block

    def run_watch_exception(self, task_function):

        try:
            task_function()
        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_exception(1)

    def job_reconnect_on_lost_chain(self):
        """ Task reconnect when lost connection on chain """

        self.run_watch_exception(self.reconnect_on_lost_chain)

    def job_price_feed(self):

        self.run_watch_exception(self.price_feed)

    def job_price_feed_backup(self):

        self.run_watch_exception(self.price_feed_backup)

    def add_jobs(self):

        # creating the alarm
        self.aws_put_metric_exception(0)

        # Reconnect on lost chain
        log.info("Jobs add reconnect on lost chain")
        self.tl._add_job(self.job_reconnect_on_lost_chain, datetime.timedelta(seconds=180))

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


class PriceFeederJobRIF(PriceFeederJobBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)

        self.init_contracts()

    def init_contracts(self):

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']
        address_mocstate = self.options['networks'][self.config_network]['addresses']['MoCState']

        self.contract_medianizer = RDOCMoCMedianizer(network_manager,
                                                     contract_address=address_medianizer).from_abi()
        self.contract_price_feed = RDOCPriceFeed(network_manager,
                                                 contract_address=address_pricefeed,
                                                 contract_address_moc_medianizer=address_medianizer).from_abi()
        self.contract_moc_state = RDOCMoCState(network_manager,
                                               contract_address=address_mocstate).from_abi()

        address_contract_moc_medianizer = Web3.toChecksumAddress(
            self.options['networks'][self.config_network]['addresses']['RIF_source_price_btc'])
        self.contract_moc_medianizer = MoCMedianizer(network_manager,
                                                     contract_address=address_contract_moc_medianizer).from_abi()

    def get_price(self):

        btc_usd_price = self.contract_moc_medianizer.price()
        btc_rif_price = decimal.Decimal(self.price_source.prices_weighted_median(btc_price_assign=btc_usd_price))

        usd_rif_price = btc_rif_price * btc_usd_price

        return usd_rif_price

    def price_feed(self):

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.config_network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        # get the last price we insert as a feeder
        last_price = decimal.Decimal(self.last_price)

        # get the price from oracle
        #last_price_oracle = self.contract_medianizer.peek()[0]
        last_price_oracle = self.contract_medianizer.price()

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        price_no_precision = self.get_price()

        # if the price is below the floor, I don't publish it
        price_floor = self.options['networks'][self.config_network].get('price_floor', None)
        if price_floor != None:
            price_floor = str(price_floor)
            ema = self.contract_moc_state.bitcoin_moving_average()
            kargs = {'ema': float(ema)}
            try:
                price_floor = decimal.Decimal(str(eval(price_floor, kargs)))
            except Exception as e:
                raise ValueError('price_floor: {}'.format(e))
        not_under_the_floor = not(price_floor and price_floor > price_no_precision)

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        # is more than 5 minutes from the last write
        is_in_time = (self.last_price_timestamp + datetime.timedelta(seconds=300) < now)

        log.info("[PRICE FEED] ORACLE: [{0:.6f}] MIN: [{1:.6f}] MAX: [{2:.6f}] "
                 "NEW: [{3:.6f}] IS IN RANGE: [{4}] IS IN TIME: [{5}]".format(
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
            if not self.is_simulation:
                self.contract_price_feed.post(price_to_set,
                                              block_expiration=block_expiration)
            else:
                log.info("[PRICE FEED] SIMULATION POST! ")

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
            log.info("[NO BACKUP MODE ACTIVATED]")


class PriceFeederJobMoC(PriceFeederJobBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)
        self.init_contracts()

    def init_contracts(self):

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']
        address_mocstate = self.options['networks'][self.config_network]['addresses']['MoCState']

        self.contract_medianizer = MoCMedianizer(network_manager,
                                                 contract_address=address_medianizer).from_abi()
        self.contract_price_feed = PriceFeed(network_manager,
                                             contract_address=address_pricefeed,
                                             contract_address_moc_medianizer=address_medianizer).from_abi()
        self.contract_moc_state = MoCState(network_manager,
                                           contract_address=address_mocstate).from_abi()

    def get_price(self):

        return decimal.Decimal(self.price_source.prices_weighted_median())

    def price_feed(self):

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.config_network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        # get the last price we insert as a feeder
        last_price = decimal.Decimal(self.last_price)

        # get the price from oracle
        #last_price_oracle = self.contract_medianizer.peek()[0]
        last_price_oracle = self.contract_medianizer.price()

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        price_no_precision = self.get_price()

        # if the price is below the floor, I don't publish it
        price_floor = self.options['networks'][self.config_network].get('price_floor', None)
        if price_floor != None:
            price_floor = str(price_floor)
            ema = self.contract_moc_state.bitcoin_moving_average()
            kargs = {'ema': float(ema)}
            try:
                price_floor = decimal.Decimal(str(eval(price_floor, kargs)))
            except Exception as e:
                raise ValueError('price_floor: {}'.format(e))
        not_under_the_floor = not(price_floor and price_floor > price_no_precision)

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        # is more than 5 minutes from the last write
        is_in_time = (self.last_price_timestamp + datetime.timedelta(seconds=300) < now)

        log.info("[PRICE FEED] ORACLE: [{0:.6f}] MIN: [{1:.6f}] MAX: [{2:.6f}] "
                 "NEW: [{3:.6f}] IS IN RANGE: [{4}] IS IN TIME: [{5}]".format(
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
            if not self.is_simulation:
                self.contract_price_feed.post(price_to_set,
                                              block_expiration=block_expiration)
            else:
                log.info("[PRICE FEED] SIMULATION POST! ")

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
            log.info("[NO BACKUP MODE ACTIVATED]")


class PriceFeederJobETH(PriceFeederJobBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)
        self.init_contracts()

    def init_contracts(self):

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']

        self.contract_medianizer = MoCMedianizer(network_manager,
                                                 contract_address=address_medianizer).from_abi()
        self.contract_price_feed = PriceFeed(network_manager,
                                             contract_address=address_pricefeed,
                                             contract_address_moc_medianizer=address_medianizer).from_abi()

    def get_price(self):

        return decimal.Decimal(self.price_source.prices_weighted_median())

    def price_feed(self):

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.config_network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        # get the last price we insert as a feeder
        last_price = decimal.Decimal(self.last_price)

        # get the price from oracle
        last_price_oracle, last_price_oracle_validity = self.contract_medianizer.peek()
        #last_price_oracle = self.contract_medianizer.price()

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        price_no_precision = self.get_price()

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        # is more than 5 minutes from the last write
        is_in_time = (self.last_price_timestamp + datetime.timedelta(seconds=300) < now)

        log.info("[PRICE FEED] ORACLE: [{0:.6f}] MIN: [{1:.6f}] MAX: [{2:.6f}] "
                 "NEW: [{3:.6f}] IS IN RANGE: [{4}] IS IN TIME: [{5}]".format(
                    last_price_oracle,
                    min_price,
                    max_price,
                    price_no_precision,
                    is_in_range,
                    is_in_time))

        # IF is in range or not in range but is in time
        if is_in_range or (not is_in_range and is_in_time) or not last_price_oracle_validity:

            # set the precision to price
            price_to_set = price_no_precision * 10 ** 18

            # submit the value to contract
            if not self.is_simulation:
                self.contract_price_feed.post(price_to_set,
                                              block_expiration=block_expiration)
            else:
                log.info("[PRICE FEED] SIMULATION POST! ")

            # save the last price to compare
            self.last_price = price_no_precision

            # save the last timestamp to compare
            self.last_price_timestamp = datetime.datetime.now()

        return price_no_precision


def options_from_config(filename='config.json'):
    """ Options from file config.json """

    with open(filename) as f:
        config_options = json.load(f)

    return config_options


if __name__ == '__main__':

    usage = '%prog [options] '
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--connection_network', action='store', dest='connection_network', type="string",
                      help='network to connect')

    parser.add_option('-e', '--config_network', action='store', dest='config_network', type="string",
                      help='enviroment to connect')

    parser.add_option('-c', '--config', action='store', dest='config', type="string",
                      help='path to config')

    (options, args) = parser.parse_args()

    if 'APP_CONFIG' in os.environ:
        config = json.loads(os.environ['APP_CONFIG'])
    else:
        if not options.config:
            # if there are no config try to read config.json from current folder
            config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
            if not os.path.isfile(config_path):
                raise Exception("Please select path to config or env APP_CONFIG. "
                                "Ex. /enviroments/moc-testnet/config.json "
                                "Full Ex.:"
                                "python price_feeder.py "
                                "--connection_network=rskTestnetPublic "
                                "--config_network=mocTestnet "
                                "--config ./enviroments/moc-testnet/config.json"
                                )
        else:
            config_path = options.config

        config = options_from_config(config_path)

    if 'APP_CONNECTION_NETWORK' in os.environ:
        connection_network = os.environ['APP_CONNECTION_NETWORK']
    else:
        if not options.connection_network:
            raise Exception("Please select connection network or env APP_CONNECTION_NETWORK. "
                            "Ex.: rskTesnetPublic. "
                            "Full Ex.:"
                            "python price_feeder.py "
                            "--connection_network=rskTestnetPublic "
                            "--config_network=mocTestnet "
                            "--config ./enviroments/moc-testnet/config.json")
        else:
            connection_network = options.connection_network

    if 'APP_CONFIG_NETWORK' in os.environ:
        config_network = os.environ['APP_CONFIG_NETWORK']
    else:
        if not options.config_network:
            raise Exception("Please select enviroment of your config or env APP_CONFIG_NETWORK. "
                            "Ex.: rdocTestnetAlpha"
                            "Full Ex.:"
                            "python price_feeder.py "
                            "--connection_network=rskTestnetPublic "
                            "--config_network=mocTestnet "
                            "--config ./enviroments/moc-testnet/config.json"
                            )
        else:
            config_network = options.config_network

    app_mode = config['networks'][config_network]['app_mode']

    if app_mode == 'MoC':
        price_feeder = PriceFeederJobMoC(config, config_network, connection_network)
        price_feeder.time_loop_start()
    elif app_mode == 'RIF':
        price_feeder = PriceFeederJobRIF(config, config_network, connection_network)
        price_feeder.time_loop_start()
    elif app_mode == 'ETH':
        price_feeder = PriceFeederJobETH(config, config_network, connection_network)
        price_feeder.time_loop_start()
    else:
        raise Exception("App mode not recognize!")
