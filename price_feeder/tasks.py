import datetime
import random

from web3 import Web3, exceptions
import decimal
from tabulate import tabulate

from moc_prices_source import get_price, \
    BTC_USD, \
    RIF_USD_B, \
    RIF_USD_T, \
    RIF_USD_TB, \
    RIF_USD_WMTB, \
    RIF_USDT, \
    ETH_BTC, \
    USDT_USD, \
    BNB_USDT

from .tasks_manager import PendingTransactionsTasksManager, on_pending_transactions
from .logger import log
from .utils import aws_put_metric_heart_beat
from .contracts import MoCMedianizer, PriceFeed, MoCState, MoCStateRRC20
from .base.main import ConnectionHelperBase


__VERSION__ = '3.0.0'


log.info("Starting Price Feeder version {0}".format(__VERSION__))


MAX_PENDING_BLOCK_TIME = 180  # in seconds


class PriceFeederTaskBase(PendingTransactionsTasksManager):

    def __init__(self, config):

        self.config = config
        self.connection_helper = ConnectionHelperBase(config)

        self.contracts_loaded = dict()

        log.info("Starting with MoC Medianizer: {}".format(self.config['addresses']['MoCMedianizer']))
        log.info("Starting with PriceFeed: {}".format(self.config['addresses']['PriceFeed']))
        log.info("Starting with App Mode: {}".format(self.config['app_mode']))
        log.info("Using CoinPair: {}".format(self.coin_pair()))

        # getting prices
        self.price_from_sources()

        # Load contracts into memory
        self.load_contracts()

        # init PendingTransactionsTasksManager
        super().__init__(self.config,
                         self.connection_helper,
                         self.contracts_loaded)

        # Add tasks
        self.schedule_tasks()

    def load_contracts(self):
        """ Load contracts from blockchain """

        log.info("Loading Contracts...")

        self.contracts_loaded["MoCMedianizer"] = MoCMedianizer(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['MoCMedianizer'])

        self.contracts_loaded["PriceFeed"] = PriceFeed(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['PriceFeed'])

    def coin_pair(self):
        """ Get coin pair from app Mode"""

        app_mode = self.config['app_mode']
        pair_option = self.config['pair_option']

        if pair_option is None:
            if app_mode == 'MoC':
                return BTC_USD
            elif app_mode == 'RIF':
                return RIF_USD_B
            elif app_mode == 'ETH':
                return ETH_BTC
            elif app_mode == 'USDT':
                return USDT_USD
            elif app_mode == 'BNB':
                return BNB_USDT
            else:
                raise Exception("App mode not recognize!")
        else:
            if pair_option == 'BTC_USD':
                return BTC_USD
            elif pair_option == 'RIF_USD_B':
                return RIF_USD_B
            elif pair_option == 'RIF_USD_T':
                return RIF_USD_T
            elif pair_option == 'RIF_USD_TB':
                return RIF_USD_TB
            elif pair_option == 'RIF_USD_WMTB':
                return RIF_USD_WMTB
            elif pair_option == 'RIF_USDT':
                return RIF_USDT
            elif pair_option == 'ETH_BTC':
                return ETH_BTC
            elif pair_option == 'USDT_USD':
                return USDT_USD
            elif pair_option == 'BNB_USDT':
                return BNB_USDT
            else:
                raise Exception("Pair option not recognize!")

    @staticmethod
    def log_info_from_sources(detail):

        table = []

        if detail['values']:
            for k, v in detail['values'].items():
                howto = 'computed for' if 'requirements' in v and v['requirements'] else 'obtained from'
                log.debug("Value {} the pair {}: {}".format(howto, k, v['weighted_median_price']))

        if detail['prices']:
            for price_source in detail['prices']:
                row = list()
                row.append(price_source['coinpair'])
                row.append(price_source['description'])
                row.append(price_source['price'])
                row.append(price_source['weighing'])
                row.append(price_source['percentual_weighing'])
                row.append(price_source['age'])
                row.append(price_source['ok'])
                row.append(price_source['last_change_timestamp'])
                table.append(row)

        if table:
            table.sort(key=lambda x: str((x[0], x[4])), reverse=True)
            log.debug("\n{}".format(tabulate(table, headers=[
                'Coinpair', 'Description', 'Price', 'Weighting', '% Weighting', 'Age', 'Ok', 'Last Change'
            ])))

        else:
            log.warn("No info from source!")

    def price_from_sources(self):

        d = {}
        try:
            result = get_price(self.coin_pair(), detail=d, ignore_zero_weighing=True)
            self.log_info_from_sources(d)

            prices_source_count = 0
            for e in d['prices']:
                if e['ok']:
                    prices_source_count += 1
                else:
                    coinpair = e['coinpair']
                    exchange = e['description']
                    error = e['error']
                    log.warning(f'{exchange} {coinpair} {error}')

            if not result or prices_source_count < self.config['min_prices_source']:
                raise Exception(f"At least we need {self.config['min_prices_source']} price sources.")

        except Exception as e:
            log.error(e, exc_info=True)
            result = None

        log.debug("Finally the value {} is used for the {} pair".format(result, self.coin_pair()))

        return result

    def post_price(
            self,
            price_no_precision,
            re_post_is_in_range,
            task_result,
            task=None,
            global_manager=None):

        web3 = self.connection_helper.connection_manager.web3

        # the tx queue is full and there is not a re-post condition, so return
        if not re_post_is_in_range and len(task_result['pending_transactions']) > 0:
            # no more pending tx
            return task_result, None

        # limit a pending transactions replace in queue
        if len(task_result['pending_transactions']) > self.config['max_pending_replace_txs'] + 1:
            log.error("Task :: {0} :: Abort! Too many pending replace transactions!".format(task.task_name))
            return task_result, None

        # max time in seconds that price is valid
        block_expiration = self.config['block_expiration']

        # get the medianizer address from options
        address_medianizer = self.config['addresses']['MoCMedianizer']

        # get gas price from node
        node_gas_price = decimal.Decimal(Web3.from_wei(web3.eth.gas_price, 'ether'))

        # fixed gas price
        gas_price = decimal.Decimal(Web3.from_wei(self.config['gas_price'], 'ether'))

        # the max value between node or fixed gas price
        using_gas_price = max(node_gas_price, gas_price)

        # Multiply factor of the using gas price
        calculated_gas_price = using_gas_price * decimal.Decimal(self.config['gas_price_multiply_factor'])
        # is a price re-post and there is a pending tx, we try to re-post the tx

        tx_info = dict()
        tx_info['is_replacement'] = False
        tx_info['gas_price'] = calculated_gas_price
        # nonce = web3.eth.get_transaction_count(
        #     self.connection_helper.connection_manager.accounts[0].address)
        nonce = web3.eth.get_transaction_count(
            self.connection_helper.connection_manager.accounts[0].address, "pending")

        if re_post_is_in_range and len(task_result['pending_transactions']) > 0:
            # only enter when there are a pending transactions in queue
            # this is a re-place tx

            # get the last pending transaction from the list of pending txs
            last_pending_tx = task_result['pending_transactions'][-1]

            # if any of the pending txs was mined the nonce increased and no other re-post can be done
            # return without saving new tx receipt, so new post can be executed
            # we are assuming that the wallet running this script is not used for others txs or the
            # probably that happen during a re-post is very low. In any case, a post always will succeed

            if nonce > last_pending_tx['nonce'] + 1:
                log.warn("Task :: {0} :: Nonce is different that in the queue of txs pending".format(task.task_name))
                return task_result, None

            nonce = last_pending_tx['nonce']

            calculated_gas_price = last_pending_tx['gas_price'] * decimal.Decimal(
                self.config['re_post_gas_price_increment'])
            tx_info['is_replacement'] = True
            tx_info['gas_price'] = calculated_gas_price

        tx_info['nonce'] = nonce

        # expiration block required the price feeder
        last_block = web3.eth.get_block(web3.eth.block_number)
        expiration = last_block.timestamp + block_expiration

        # set the precision to price
        price_to_set = price_no_precision * 10 ** 18

        # send transaction to the price feeder
        tx_hash = self.contracts_loaded["PriceFeed"].post(
            int(price_to_set),
            int(expiration),
            Web3.to_checksum_address(address_medianizer),
            gas_limit=self.config['tasks']['price_feed']['gas_limit'],
            gas_price=int(calculated_gas_price * 10 ** 18),
            nonce=nonce
        )

        # save the last price to compare
        global_manager['last_price'] = price_no_precision

        # save the last timestamp to compare
        global_manager['last_price_timestamp'] = datetime.datetime.now()

        tx_info['hash'] = tx_hash
        tx_info['timestamp'] = datetime.datetime.now()

        if tx_info['is_replacement']:
            caption_log = 'Sending Replace TX'
        else:
            caption_log = 'Sending TX'

        log.info("Task :: {0} :: {1} :: Hash: [{2}] Nonce: [{3}] Gas Price: [{4}]".format(task.task_name,
                                                                                          caption_log,
                                                                                          Web3.to_hex(tx_info['hash']),
                                                                                          tx_info['nonce'],
                                                                                          int(calculated_gas_price*10**18)))

        return task_result, tx_info

    @on_pending_transactions
    def task_price_feed(self, task=None, global_manager=None, task_result=None):

        if not task_result:
            task_result = dict()

        if not isinstance(task_result, dict):
            raise Exception("Task result must be dict type")

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation_write_blockchain = self.config['price_variation_write_blockchain']

        # re post price variation accepted
        price_variation_re_write_blockchain = self.config['price_variation_re_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.config['block_expiration']

        timeout_in_time = abs(block_expiration - MAX_PENDING_BLOCK_TIME)

        # get the last price we insert as a feeder can be in pending state
        if 'last_price' in global_manager:
            last_price = decimal.Decimal(global_manager['last_price'])
        else:
            last_price = decimal.Decimal(0)

        if 'last_price_timestamp' in global_manager:
            last_price_timestamp = global_manager['last_price_timestamp']
        else:
            last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=timeout_in_time + 1)

        # get new price from source
        price_no_precision = self.price_from_sources()
        # price_no_precision = decimal.Decimal(round(random.uniform(0.06990, 0.06975), 5))

        if not price_no_precision:
            # when no price finish task and put an alarm
            log.error("Task :: {0} :: No price source!.".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS
            return task_result

        # get the price from oracle and validity of the same
        last_price_oracle, last_price_oracle_validity = self.contracts_loaded['MoCMedianizer'].peek()
        if not last_price_oracle_validity:
            # cannot contact medianizer but we continue to put price
            log.error("Task :: {0} :: CANNOT GET MEDIANIZER PRICE! ".format(task.task_name))
            #aws_put_metric_heart_beat(1)  # Put an alarm in AWS

        # calculate the price variation from the last price from oracle
        price_variation_oracle = abs((price_no_precision / last_price_oracle) - 1)

        # Accepted variation to write to blockchain
        is_in_range = price_variation_oracle >= decimal.Decimal(price_variation_write_blockchain)

        # calculate the price variation from the last price published
        if last_price != 0:
            last_price_variation = abs((price_no_precision / last_price) - 1)
        else:
            last_price_variation = decimal.Decimal(0)

        # Accepted variation to re-write to blockchain
        re_post_is_in_range = last_price_variation >= decimal.Decimal(price_variation_re_write_blockchain)

        td_delta = now - last_price_timestamp

        # is more than 5 minutes from the last write
        is_in_time = (last_price_timestamp + datetime.timedelta(seconds=timeout_in_time) < now)

        if task_result.get('pending_transactions', None):
            count_pending_txs = len(task_result['pending_transactions'])
        else:
            count_pending_txs = 0

        log.info("Task :: {0} :: Evaluate Price :: "
                 "Price Oracle: [{1:.6f}] "
                 "Price Last Time: [{2:.6f}] "
                 "Price New: [{3:.6f}] "
                 "Is in range: [{4}] "
                 "Is in range replace: [{5}] "
                 "Is in time: [{6}] "
                 "Variation Oracle: [{7:.6}%] "
                 "Variation Last Time: [{8:.6}%] "
                 "Last write ago: [{9}] "
                 "Pending Txs: [{10}]".format(
            task.task_name,
            last_price_oracle,
            last_price,
            price_no_precision,
            is_in_range,
            re_post_is_in_range,
            is_in_time,
            price_variation_oracle * 100,
            last_price_variation * 100,
            td_delta.seconds,
            count_pending_txs))

        # IF is in range or not in range but is in time
        is_post = is_in_range or (not is_in_range and is_in_time) or not last_price_oracle_validity
        if is_post or re_post_is_in_range:
            # submit the value to contract
            if not self.config['is_simulation']:
                task_result, tx_info = self.post_price(
                    price_no_precision,
                    re_post_is_in_range,
                    task_result,
                    task=task,
                    global_manager=global_manager)

                if tx_info:
                    new_tx_dict = dict()
                    new_tx_dict['price_oracle'] = last_price_oracle
                    new_tx_dict['price_last_time'] = last_price
                    new_tx_dict['price_new'] = price_no_precision
                    new_tx_dict['variation_oracle'] = price_variation_oracle * 100
                    new_tx_dict['variation_last_time'] = last_price_variation * 100
                    new_tx_dict['hash'] = tx_info['hash']
                    new_tx_dict['is_replacement'] = tx_info['is_replacement']
                    new_tx_dict['timestamp'] = tx_info['timestamp']
                    new_tx_dict['gas_price'] = tx_info['gas_price']
                    new_tx_dict['nonce'] = tx_info['nonce']

                    task_result['pending_transactions'].append(new_tx_dict)

            else:
                log.info("Task :: {0} :: Simulation Post! ".format(task.task_name))

        return task_result

    def schedule_tasks(self):

        log.info("Starting adding jobs...")

        # creating the alarm
        aws_put_metric_heart_beat(0)

        # set max workers
        self.max_workers = 1

        log.info("Job add: 1. Price Feeder")
        self.add_task(self.task_price_feed,
                      args=[],
                      wait=self.config['tasks']['price_feed']['interval'],
                      timeout=self.config['tasks']['price_feed']['wait_timeout'],
                      task_name='1. Price Feeder')

        # Set max workers
        self.max_tasks = len(self.tasks)


class PriceFeederTaskMoC(PriceFeederTaskBase):

    def __init__(self, config):

        super().__init__(config)


class PriceFeederTaskRIF(PriceFeederTaskBase):

    def __init__(self, config):

        super().__init__(config)

    def load_contracts(self):
        """Get contracts from blockchain"""

        log.info("Loading Contracts...")

        self.contracts_loaded["MoCMedianizer"] = MoCMedianizer(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['MoCMedianizer'])

        self.contracts_loaded["PriceFeed"] = PriceFeed(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['PriceFeed'])

        self.contracts_loaded["MoCState"] = MoCStateRRC20(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['MoCState'])

    @on_pending_transactions
    def task_price_feed(self, task=None, global_manager=None, task_result=None):

        if not task_result:
            task_result = dict()

        if not isinstance(task_result, dict):
            raise Exception("Task result must be dict type")

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation_write_blockchain = self.config['price_variation_write_blockchain']

        # re post price variation accepted
        price_variation_re_write_blockchain = self.config['price_variation_re_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.config['block_expiration']

        timeout_in_time = abs(block_expiration - MAX_PENDING_BLOCK_TIME)

        # get the last price we insert as a feeder can be in pending state
        if 'last_price' in global_manager:
            last_price = decimal.Decimal(global_manager['last_price'])
        else:
            last_price = decimal.Decimal(0)

        if 'last_price_timestamp' in global_manager:
            last_price_timestamp = global_manager['last_price_timestamp']
        else:
            last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=timeout_in_time + 1)

        price_no_precision = self.price_from_sources()
        #price_no_precision = decimal.Decimal(round(random.uniform(0.06990, 0.06975), 5))

        if not price_no_precision:
            # when no price finish task and put an alarm
            log.error("Task :: {0} :: No price source!.".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS
            return task_result

        # get the price from oracle and validity of the same
        last_price_oracle, last_price_oracle_validity = self.contracts_loaded['MoCMedianizer'].peek()
        if not last_price_oracle_validity:
            # cannot contact medianizer but we continue to put price
            log.error("Task :: {0} :: Price from medianizer is invalid! ".format(task.task_name))
            #aws_put_metric_heart_beat(1)  # Put an alarm in AWS

        # calculate the price variation from the last price from oracle
        price_variation_oracle = abs((price_no_precision / last_price_oracle) - 1)

        # if the price is below the floor, I don't publish it
        ema = self.contracts_loaded['MoCState'].price_moving_average()
        price_floor = ema * decimal.Decimal(0.193)
        under_the_floor = price_floor and price_floor > price_no_precision
        if under_the_floor:
            log.error("Task :: {0} :: Price under the floor!. Price: {1} Price Floor: {2} ".format(
                task.task_name,
                price_no_precision,
                price_floor))
            return task_result

        # Accepted variation to write to blockchain
        is_in_range = price_variation_oracle >= decimal.Decimal(price_variation_write_blockchain)

        # calculate the price variation from the last price published
        if last_price != 0:
            last_price_variation = abs((price_no_precision / last_price) - 1)
        else:
            last_price_variation = decimal.Decimal(0)

        # Accepted variation to re-write to blockchain
        re_post_is_in_range = last_price_variation >= decimal.Decimal(price_variation_re_write_blockchain)

        td_delta = now - last_price_timestamp

        # is more than 5 minutes from the last write
        is_in_time = (last_price_timestamp + datetime.timedelta(seconds=timeout_in_time) < now)

        if task_result.get('pending_transactions', None):
            count_pending_txs = len(task_result['pending_transactions'])
        else:
            count_pending_txs = 0

        log.info("Task :: {0} :: Evaluate Price :: "
                 "Price Oracle: [{1:.6f}] "
                 "Price Last Time: [{2:.6f}] "
                 "Price New: [{3:.6f}] "
                 "Is in range: [{4}] "
                 "Is in range replace: [{5}] "
                 "Is in time: [{6}] "
                 "Variation Oracle: [{7:.6}%] "
                 "Variation Last Time: [{8:.6}%] "
                 "Floor: [{9:.6}] "
                 "Last write ago: [{10}] "
                 "Pending Txs: [{11}]".format(
            task.task_name,
                  last_price_oracle,
                  last_price,
                  price_no_precision,
                  is_in_range,
                  re_post_is_in_range,
                  is_in_time,
                  price_variation_oracle*100,
                  last_price_variation*100,
                  price_floor,
                  td_delta.seconds,
                  count_pending_txs))

        # IF is in range or not in range but is in time
        is_post = is_in_range or (not is_in_range and is_in_time) or not last_price_oracle_validity
        if is_post or re_post_is_in_range:
            # submit the value to contract if not a simulation
            if not self.config['is_simulation']:
                task_result, tx_info = self.post_price(
                    price_no_precision,
                    re_post_is_in_range,
                    task_result,
                    task=task,
                    global_manager=global_manager)

                if tx_info:
                    new_tx_dict = dict()
                    new_tx_dict['price_oracle'] = last_price_oracle
                    new_tx_dict['price_last_time'] = last_price
                    new_tx_dict['price_new'] = price_no_precision
                    new_tx_dict['variation_oracle'] = price_variation_oracle * 100
                    new_tx_dict['variation_last_time'] = last_price_variation * 100
                    new_tx_dict['hash'] = tx_info['hash']
                    new_tx_dict['is_replacement'] = tx_info['is_replacement']
                    new_tx_dict['timestamp'] = tx_info['timestamp']
                    new_tx_dict['gas_price'] = tx_info['gas_price']
                    new_tx_dict['nonce'] = tx_info['nonce']

                    task_result['pending_transactions'].append(new_tx_dict)

            else:
                log.info("Task :: {0} :: Simulation Post! ".format(task.task_name))

        return task_result


class PriceFeederTaskETH(PriceFeederTaskBase):

    def __init__(self, config):

        super().__init__(config)


class PriceFeederTaskUSDT(PriceFeederTaskBase):

    def __init__(self, config):

        super().__init__(config)


class PriceFeederTaskBNB(PriceFeederTaskBase):

    def __init__(self, config):

        super().__init__(config)
