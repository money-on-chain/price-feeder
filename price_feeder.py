import os
from optparse import OptionParser
import datetime
import json
from timeloop import Timeloop
from web3 import Web3
import boto3
import time

# local imports
from node_manager import NodeManager
from price_engines import PriceEngines

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


class ContractManager(NodeManager):

    def __init__(self, config_options, network_nm):
        self.options = config_options
        self.PriceFeed = None
        super(NodeManager, self).__init__(options=config_options, network=network_nm)

    def connect_contract(self):
        self.connect_node()
        self.load_contracts()

    def load_contracts(self):

        path_build = self.options['build_dir']
        address_price_feed = self.options['networks'][network]['addresses']['PriceFeed']

        self.PriceFeed = self.load_json_contract(os.path.join(path_build, "PriceFeed.json"),
                                                 deploy_address=address_price_feed)

    def post_price(self, p_price):

        self.connect_contract()

        address_moc_medianizer = Web3.toChecksumAddress(self.options['networks'][network]['addresses']['MoCMedianizer'])

        delay = self.options['block_expiration']
        last_block = self.get_block('latest')
        expiration = last_block.timestamp + delay
        try:
            tx_hash = self.fnx_transaction(self.PriceFeed, 'post',
                                           int(p_price),
                                           int(expiration),
                                           address_moc_medianizer)
            tx_receipt = self.wait_transaction_receipt(tx_hash)

        except Exception as e:
            log.error(e, exc_info=True)
            self.aws_put_metric_heart_beat(0)
        else:
            log.debug(tx_receipt)
            log.info("SUCCESS!. Price Set: [{0}]".format(p_price))
            self.aws_put_metric_heart_beat(1)

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


class PriceFeederJob:

    def __init__(self, path_to_config, network_nm, build_dir_nm):

        self.tl = Timeloop()
        self.last_price = 0.0

        config_options = self.options_from_config(path_to_config)
        config_options['build_dir'] = build_dir_nm
        self.options = config_options

        #self.nm = NodeManager(options=config_options, network=network_nm)
        self.cm = ContractManager(config_options, network_nm)

        if self.options['app_mode'] == 'MoC':
            self.price_source = PriceEngines(self.options['price_engines'], log=log)
        elif self.options['app_mode'] == 'rrc20':
            raise Exception("Error! Config app_mode not recognize!")
        else:
            raise Exception("Error! Config app_mode not recognize!")

    @staticmethod
    def options_from_config(filename='config.json'):
        """ Options from file config.json """

        with open(filename) as f:
            config_options = json.load(f)

        return config_options

    def price_feed(self):

        last_price = self.last_price
        price_variation_accepted = self.options['price_variation_accepted'] * last_price
        min_price = abs(last_price - price_variation_accepted)
        max_price = last_price + price_variation_accepted

        price_medianizer = self.price_source.prices_weighted_median()

        price_to_set = price_medianizer * 10 ** 18
        log.debug("Last price: [{0}] Min: [{1}] Max: [{2}] New price: [{3}]".format(last_price,
                                                                                    min_price,
                                                                                    max_price,
                                                                                    price_medianizer))
        if price_medianizer < min_price or price_medianizer > max_price:
            self.cm.post_price(price_to_set)
        else:
            log.info("WARNING! NOT SETTING is the same to last +- variation! [{0}]".format(price_medianizer))
            self.cm.aws_put_metric_heart_beat(1)
        
        self.last_price = price_medianizer

        return price_medianizer

    def job_price_feed(self):

        try:
            self.price_feed()
        except Exception as e:
            log.error(e, exc_info=True)

    def add_jobs(self):

        self.tl._add_job(self.job_price_feed, datetime.timedelta(seconds=self.options['interval']))

    def time_loop_start(self):

        self.add_jobs()
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

    price_feeder = PriceFeederJob(config_path, network, build_dir)
    price_feeder.time_loop_start()
