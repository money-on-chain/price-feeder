import datetime

from web3 import Web3, exceptions
import decimal
from tabulate import tabulate

from moneyonchain.networks import network_manager, web3, chain
from moneyonchain.rdoc import RDOCMoCState
from moneyonchain.medianizer import MoCMedianizer, PriceFeed, RDOCMoCMedianizer, RDOCPriceFeed, \
    ETHMoCMedianizer, ETHPriceFeed, USDTMoCMedianizer, USDTPriceFeed
from moneyonchain.transaction import receipt_to_log

from moc_prices_source import get_price, BTC_USD, RIF_USD, ETH_BTC, USDT_USD

from .tasks_manager import TasksManager
from .logger import log
from .utils import aws_put_metric_heart_beat


__VERSION__ = '2.1.5'


log.info("Starting Price Feeder version {0}".format(__VERSION__))


MAX_PENDING_BLOCK_TIME = 180  # in seconds


def pending_queue_is_full(account_index=0):

    # get first account
    account_address = network_manager.accounts[account_index].address

    nonce = web3.eth.getTransactionCount(account_address, 'pending')
    last_used_nonce = web3.eth.getTransactionCount(account_address)

    # A limit of pending on blockchain
    if nonce >= last_used_nonce + 1:
        log.info('Cannot create more transactions for {} as the node queue will be full. Nonce: [{}] '
                 'Last used Nonce: [{}]'.format(
                  account_address, nonce, last_used_nonce))
        return True

    return False


def save_pending_tx_receipt(tx_receipt, task_name):
    """ Tx receipt """

    result = dict()
    result['receipt'] = dict()

    if tx_receipt is None:
        result['receipt']['id'] = None
        result['receipt']['timestamp'] = None
        return result

    result['receipt']['id'] = tx_receipt.txid
    result['receipt']['timestamp'] = datetime.datetime.now()

    log.info("Task :: {0} :: Sending tx: {1}".format(task_name, tx_receipt.txid))

    return result


def pending_transaction_receipt(task):
    """ Wait to pending receipt get confirmed"""

    timeout_reverted = 600

    result = dict()
    if task.tx_receipt:
        result['receipt'] = dict()
        result['receipt']['confirmed'] = False
        result['receipt']['reverted'] = False

        try:
            tx_rcp = chain.get_transaction(task.tx_receipt)
        except exceptions.TransactionNotFound:
            # Transaction not exist anymore, blockchain reorder?
            # timeout and permit to send again transaction
            result['receipt']['id'] = None
            result['receipt']['timestamp'] = None
            result['receipt']['confirmed'] = True

            log.error("Task :: {0} :: Transaction not found! {1}".format(task.task_name, task.tx_receipt))

            return result

        # pending state
        # Status:
        #    Dropped = -2
        #    Pending = -1
        #    Reverted = 0
        #    Confirmed = 1

        # confirmed state
        if tx_rcp.confirmations >= 1 and tx_rcp.status == 1:

            result['receipt']['confirmed'] = True
            result['receipt']['id'] = None
            result['receipt']['timestamp'] = None

            log.info("Task :: {0} :: Confirmed tx! [{1}]".format(task.task_name, task.tx_receipt))

        # reverted
        elif tx_rcp.confirmations >= 1 and tx_rcp.status == 0:

            result['receipt']['confirmed'] = True
            result['receipt']['reverted'] = True

            elapsed = datetime.datetime.now() - task.tx_receipt_timestamp
            timeout = datetime.timedelta(seconds=timeout_reverted)

            log.error("Task :: {0} :: Reverted tx! [{1}] Elapsed: [{2}] Timeout: [{3}]".format(
                task.task_name, task.tx_receipt, elapsed.seconds, timeout_reverted))

            if elapsed > timeout:
                # timeout allow to send again transaction on reverted
                result['receipt']['id'] = None
                result['receipt']['timestamp'] = None
                result['receipt']['confirmed'] = True

                log.error("Task :: {0} :: Timeout Reverted tx! [{1}]".format(task.task_name, task.tx_receipt))

        elif tx_rcp.confirmations < 1 and tx_rcp.status < 0:
            elapsed = datetime.datetime.now() - task.tx_receipt_timestamp
            timeout = datetime.timedelta(seconds=task.timeout)

            if elapsed > timeout:
                # timeout allow to send again transaction
                result['receipt']['id'] = None
                result['receipt']['timestamp'] = None
                result['receipt']['confirmed'] = True

                log.error("Task :: {0} :: Timeout tx! [{1}]".format(task.task_name, task.tx_receipt))
            else:
                log.info("Task :: {0} :: Pending tx state ... [{1}]".format(task.task_name, task.tx_receipt))

    return result


def task_reconnect_on_lost_chain(task=None, global_manager=None):

    # get las block query last time from task result of the run last time task
    if task.result:
        last_block = task.result
    else:
        last_block = 0

    block = network_manager.block_number

    if not last_block:
        log.info("Task :: Reconnect on lost chain :: Ok :: [{0}/{1}]".format(
            last_block, block))
        last_block = block

        return last_block

    if block <= last_block:
        # this means no new blocks from the last call,
        # so this means a halt node, try to reconnect.

        log.error("Task :: Reconnect on lost chain :: "
                  "[ERROR] :: Same block from the last time! Terminate Task Manager! [{0}/{1}]".format(
                    last_block, block))

        # Put alarm in aws
        aws_put_metric_heart_beat(1)

        # terminate job
        return dict(shutdown=True)

    log.info("Task :: Reconnect on lost chain :: Ok :: [{0}/{1}]".format(
        last_block, block))

    # save the last block
    last_block = block

    return last_block


class PriceFeederTaskBase(TasksManager):

    def __init__(self, app_config, config_net, connection_net):

        super().__init__()

        self.options = app_config
        self.config_network = config_net
        self.connection_network = connection_net

        self.app_mode = self.options['networks'][self.config_network]['app_mode']

        try:
            self.min_prices_source = self.options['networks'][self.config_network]['min_prices_source']
        except KeyError:
            self.min_prices_source = 1

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

        log.info("Starting with MoC Medianizer: {}".format(address_medianizer))
        log.info("Starting with PriceFeed: {}".format(address_pricefeed))
        log.info("Starting with App Mode: {}".format(self.app_mode))
        log.info("Using CoinPair: {}".format(self.coinpair()))
        self.price_from_sources()

        # simulation don't write to blockchain
        self.is_simulation = False
        if 'is_simulation' in self.options:
            self.is_simulation = self.options['is_simulation']

        # connect
        self.connect()

        # Add tasks
        self.schedule_tasks()

    def connect(self):
        """ Init connection"""

        # Connect to network
        network_manager.connect(
            connection_network=self.connection_network,
            config_network=self.config_network)

    def coinpair(self):
        """ Get coinpair from app Mode"""

        if self.app_mode == 'MoC':
            return BTC_USD
        elif self.app_mode == 'RIF':
            return RIF_USD
        elif self.app_mode == 'ETH':
            return ETH_BTC
        elif self.app_mode == 'USDT':
            return USDT_USD
        else:
            raise Exception("App mode not recognize!")

    def contracts(self):
        """Get contracts from blockchain"""

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']

        if self.app_mode == 'MoC':
            contract_medianizer = MoCMedianizer(network_manager,
                                                contract_address=address_medianizer).from_abi()
            contract_price_feed = PriceFeed(network_manager,
                                            contract_address=address_pricefeed,
                                            contract_address_moc_medianizer=address_medianizer).from_abi()
        elif self.app_mode == 'RIF':
            contract_medianizer = RDOCMoCMedianizer(network_manager,
                                                    contract_address=address_medianizer).from_abi()
            contract_price_feed = RDOCPriceFeed(network_manager,
                                                contract_address=address_pricefeed,
                                                contract_address_moc_medianizer=address_medianizer).from_abi()
        elif self.app_mode == 'ETH':
            contract_medianizer = ETHMoCMedianizer(network_manager,
                                                   contract_address=address_medianizer).from_abi()
            contract_price_feed = ETHPriceFeed(network_manager,
                                               contract_address=address_pricefeed,
                                               contract_address_moc_medianizer=address_medianizer).from_abi()
        elif self.app_mode == 'USDT':
            contract_medianizer = USDTMoCMedianizer(network_manager,
                                                    contract_address=address_medianizer).from_abi()
            contract_price_feed = USDTPriceFeed(network_manager,
                                                contract_address=address_pricefeed,
                                                contract_address_moc_medianizer=address_medianizer).from_abi()
        else:
            raise Exception("App mode not recognize!")

        return dict(medianizer=contract_medianizer, price_feed=contract_price_feed)

    @staticmethod
    def log_info_from_sources(detail):

        table = []
        if detail['prices']:
            count = 0
            for price_source in detail['prices']:
                count += 1
                row = list()
                row.append(count)
                row.append(price_source['description'])
                row.append(price_source['price'])
                row.append(price_source['weighing'])
                row.append(price_source['percentual_weighing'])
                row.append(price_source['age'])
                row.append(price_source['ok'])
                row.append(price_source['last_change_timestamp'])
                table.append(row)
        if table:
            table.sort(key=lambda x: str(x[3]), reverse=True)
            log.info("\n{}".format(tabulate(table, headers=[
                '', 'Description', 'Price', 'Weighting', '% Weighting', 'Age', 'Ok', 'Last Change'
            ])))
        else:
            log.warn("No info from source!")

    def price_from_sources(self):

        d = {}
        try:
            result = get_price(self.coinpair(), detail=d)
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

            if not result or prices_source_count < self.min_prices_source:
                raise Exception(f"At least we need {self.min_prices_source} price sources.")

        except Exception as e:
            log.error(e, exc_info=True)
            result = None

        return result

    def post_price(self, price_no_precision, info_contracts, task=None):

        # Not call until tx confirmated!
        pending_tx_receipt = pending_transaction_receipt(task)
        if 'receipt' in pending_tx_receipt:
            if not pending_tx_receipt['receipt']['confirmed'] or pending_tx_receipt['receipt']['reverted']:
                # Continue on pending status or reverted
                return pending_tx_receipt

        if pending_queue_is_full():
            log.error("Task :: {0} :: Pending queue is full".format(task.task_name))
            aws_put_metric_heart_beat(1)
            return

        # set the maximum gas limit
        gas_limit = self.options['gas_limit']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        # get the medianizer address from options
        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']

        # arguments to pass to tx
        tx_args = info_contracts['price_feed'].tx_arguments(gas_limit=gas_limit, required_confs=0)

        # expiration block required the price feeder
        last_block = web3.eth.getBlock(web3.eth.blockNumber)
        expiration = last_block.timestamp + block_expiration

        # set the precision to price
        price_to_set = price_no_precision * 10 ** 18

        # check estimate gas is greater than gas limit
        estimate_gas = info_contracts['price_feed'].sc.post.estimate_gas(
            int(price_to_set),
            int(expiration),
            Web3.toChecksumAddress(address_medianizer),
            tx_args)
        if estimate_gas > gas_limit:
            log.error("Task :: {0} :: Estimate gas is > to gas limit. No send tx".format(task.task_name))
            aws_put_metric_heart_beat(1)
            return

        # send transaction to the price feeder
        tx_receipt = info_contracts['price_feed'].sc.post(
            int(price_to_set),
            int(expiration),
            Web3.toChecksumAddress(address_medianizer),
            tx_args)

        return save_pending_tx_receipt(tx_receipt, task.task_name)

    def task_price_feed(self, task=None, global_manager=None):

        result = dict()

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.config_network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        timeout_in_time = abs(block_expiration - MAX_PENDING_BLOCK_TIME)

        # get the last price we insert as a feeder
        if 'last_price' in global_manager:
            last_price = decimal.Decimal(global_manager['last_price'])
        else:
            last_price = decimal.Decimal(0)

        if 'last_price_timestamp' in global_manager:
            last_price_timestamp = global_manager['last_price_timestamp']
        else:
            last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=timeout_in_time + 1)

        # read contracts
        info_contracts = self.contracts()

        # get the price from oracle and validity of the same
        last_price_oracle, last_price_oracle_validity = info_contracts['medianizer'].peek()
        if not last_price_oracle_validity:
            # cannot contact medianizer but we continue to put price
            log.error("Task :: {0} :: CANNOT GET MEDIANIZER PRICE! ".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        price_no_precision = self.price_from_sources()

        if not price_no_precision:
            # when no price finish task and put an alarm
            log.error("Task :: {0} :: No price source!.".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS
            return result

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        # is more than 5 minutes from the last write
        is_in_time = (last_price_timestamp + datetime.timedelta(seconds=timeout_in_time) < now)

        td_delta = now - last_price_timestamp

        log.info("Task :: {0} :: Oracle: [{1:.6f}] Last: [{2:.6f}] "
                 "New: [{3:.6f}] Is in range: [{4}] Is in time: [{5}] Last write ago: [{6}]".format(
            task.task_name,
            last_price_oracle,
            last_price,
            price_no_precision,
            is_in_range,
            is_in_time,
            td_delta.seconds))

        # IF is in range or not in range but is in time
        if is_in_range or (not is_in_range and is_in_time) or not last_price_oracle_validity:

            # submit the value to contract
            if not self.is_simulation:
                result = self.post_price(price_no_precision, info_contracts, task=task)
            else:
                log.info("Task :: {0} :: Simulation Post! ".format(task.task_name))

            # save the last price to compare
            global_manager['last_price'] = price_no_precision

            # save the last timestamp to compare
            global_manager['last_price_timestamp'] = datetime.datetime.now()

        if result:
            return result
        else:
            return save_pending_tx_receipt(None, task.task_name)

    def task_price_feed_backup(self, task=None, global_manager=None):
        """ Only start to work only when we dont have price """

        result = dict()

        # get the last price we insert as a feeder
        if 'backup_writes' in global_manager:
            backup_writes = global_manager['backup_writes']
        else:
            backup_writes = 0

        # read contracts
        info_contracts = self.contracts()

        if not info_contracts['medianizer'].compute()[1] or backup_writes > 0:

            result = self.task_price_feed(task=task, global_manager=global_manager)

            aws_put_metric_heart_beat(1)

            if backup_writes <= 0:
                if 'backup_writes' in self.options:
                    backup_writes = self.options['backup_writes']
                else:
                    backup_writes = 100

            backup_writes -= 1

            log.error("Task :: {0} :: BACKUP MODE ACTIVATED! WRITE REMAINING:{1}".format(task.task_name,
                                                                                         backup_writes))

        else:
            log.info("Task :: {0} :: [NO BACKUP MODE ACTIVATED]".format(task.task_name))

        # Save backup writes to later use
        global_manager['backup_writes'] = backup_writes

        if result:
            return result
        else:
            return save_pending_tx_receipt(None, task.task_name)

    def task_contract_oracle_poke(self, task=None, global_manager=None):

        # Not call until tx confirmated!
        pending_tx_receipt = pending_transaction_receipt(task)
        if 'receipt' in pending_tx_receipt:
            if not pending_tx_receipt['receipt']['confirmed'] or pending_tx_receipt['receipt']['reverted']:
                # Continue on pending status or reverted
                return pending_tx_receipt

        # set the maximum gas limit
        gas_limit = self.options['gas_limit']

        # read contracts
        info_contracts = self.contracts()

        price_validity = info_contracts['medianizer'].peek()[1]
        if not info_contracts['medianizer'].compute()[1] and price_validity:

            if pending_queue_is_full():
                log.error("Task :: {0} :: Pending queue is full".format(task.task_name))
                aws_put_metric_heart_beat(1)
                return

            tx_args = info_contracts['medianizer'].tx_arguments(gas_limit=gas_limit, required_confs=0)

            # check estimate gas is greater than gas limit
            estimate_gas = info_contracts['medianizer'].sc.poke.estimate_gas(tx_args)
            if estimate_gas > gas_limit:
                log.error("Task :: {0} :: Estimate gas is > to gas limit. No send tx".format(task.task_name))
                aws_put_metric_heart_beat(1)
                return

            tx_receipt = info_contracts['medianizer'].sc.poke(tx_args)
            log.error("Task :: {0} :: Not valid price! Disabling Price!".format(task.task_name))
            aws_put_metric_heart_beat(1)

            return save_pending_tx_receipt(tx_receipt, task.task_name)

        # if no valid price in oracle please send alarm
        if not price_validity:
            log.error("Task :: {0} :: No valid price in oracle!".format(task.task_name))
            aws_put_metric_heart_beat(1)

        log.info("Task :: {0} :: No!".format(task.task_name))
        return save_pending_tx_receipt(None, task.task_name)

    def schedule_tasks(self):

        log.info("Starting adding jobs...")

        # creating the alarm
        aws_put_metric_heart_beat(0)

        # set max workers
        self.max_workers = 1

        # Reconnect on lost chain
        log.info("Job add: 99. Reconnect on lost chain")
        self.add_task(task_reconnect_on_lost_chain, args=[], wait=180, timeout=180)

        backup_mode = False
        if 'backup_mode' in self.options:
            if self.options['backup_mode']:
                backup_mode = True

        if backup_mode:
            log.info("Job add: 2. Price feeder as BACKUP!")
            self.add_task(self.task_price_feed_backup,
                          args=[],
                          wait=self.options['interval'],
                          timeout=180,
                          task_name='2. Price feeder as BACKUP')
        else:
            log.info("Job add: 1. Price Feeder")
            self.add_task(self.task_price_feed,
                          args=[],
                          wait=self.options['interval'],
                          timeout=180,
                          task_name='1. Price Feeder')

        # oracle poke disable price when something happend on source exchanges
        # prefered to disabled price validity
        log.info("Job add: 3. Oracle Poke [disable price]")
        self.add_task(self.task_contract_oracle_poke,
                      args=[],
                      wait=60,
                      timeout=180,
                      task_name='3. Oracle Poke [disable price]')

        # Set max workers
        self.max_tasks = len(self.tasks)


class PriceFeederTaskMoC(PriceFeederTaskBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)


class PriceFeederTaskRIF(PriceFeederTaskBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)

    def contracts(self):
        """Get contracts from blockchain"""

        address_medianizer = self.options['networks'][self.config_network]['addresses']['MoCMedianizer']
        address_pricefeed = self.options['networks'][self.config_network]['addresses']['PriceFeed']
        address_mocstate = self.options['networks'][self.config_network]['addresses']['MoCState']

        contract_medianizer = RDOCMoCMedianizer(network_manager,
                                                contract_address=address_medianizer).from_abi()
        contract_price_feed = RDOCPriceFeed(network_manager,
                                            contract_address=address_pricefeed,
                                            contract_address_moc_medianizer=address_medianizer).from_abi()
        contract_moc_state = RDOCMoCState(network_manager,
                                          contract_address=address_mocstate).from_abi()

        return dict(medianizer=contract_medianizer, price_feed=contract_price_feed, moc_state=contract_moc_state)

    def task_price_feed(self, task=None, global_manager=None):

        result = dict()

        # now
        now = datetime.datetime.now()

        # price variation accepted
        price_variation = self.options['networks'][self.config_network]['price_variation_write_blockchain']

        # max time in seconds that price is valid
        block_expiration = self.options['networks'][self.config_network]['block_expiration']

        timeout_in_time = abs(block_expiration - MAX_PENDING_BLOCK_TIME)

        # get the last price we insert as a feeder
        if 'last_price' in global_manager:
            last_price = decimal.Decimal(global_manager['last_price'])
        else:
            last_price = decimal.Decimal(0)

        if 'last_price_timestamp' in global_manager:
            last_price_timestamp = global_manager['last_price_timestamp']
        else:
            last_price_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=timeout_in_time + 1)

        # read contracts
        info_contracts = self.contracts()

        # get the price from oracle and validity of the same
        last_price_oracle, last_price_oracle_validity = info_contracts['medianizer'].peek()
        if not last_price_oracle_validity:
            # cannot contact medianizer but we continue to put price
            log.error("Task :: {0} :: CANNOT GET MEDIANIZER PRICE! ".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS

        # calculate the price variation from the last price from oracle
        price_variation_accepted = decimal.Decimal(price_variation) * last_price_oracle

        min_price = abs(last_price_oracle - price_variation_accepted)
        max_price = last_price_oracle + price_variation_accepted

        price_no_precision = self.price_from_sources()

        if not price_no_precision:
            # when no price finish task and put an alarm
            log.error("Task :: {0} :: No price source!.".format(task.task_name))
            aws_put_metric_heart_beat(1)  # Put an alarm in AWS
            return result

        # if the price is below the floor, I don't publish it
        ema = info_contracts['moc_state'].bitcoin_moving_average()
        price_floor = ema * decimal.Decimal(0.193)
        under_the_floor = price_floor and price_floor > price_no_precision
        if under_the_floor:
            log.error("Task :: {0} :: Price under the floor!. Price: {1} Price Floor: {2} ".format(
                task.task_name,
                price_no_precision,
                price_floor))
            return result

        # is outside the range so we need to write to blockchain
        is_in_range = price_no_precision < min_price or price_no_precision > max_price

        td_delta = now - last_price_timestamp

        # is more than 5 minutes from the last write
        is_in_time = (last_price_timestamp + datetime.timedelta(seconds=timeout_in_time) < now)

        log.info("Task :: {0} :: Oracle: [{1:.6f}] Last: [{2:.6f}] "
                 "New: [{3:.6f}] Is in range: [{4}] Is in time: [{5}] Floor: [{6:.6}] Last write ago: [{7}]".format(
            task.task_name,
            last_price_oracle,
            last_price,
            price_no_precision,
            is_in_range,
            is_in_time,
            price_floor,
            td_delta.seconds))

        # IF is in range or not in range but is in time
        if is_in_range or (not is_in_range and is_in_time) or not last_price_oracle_validity:

            # submit the value to contract
            if not self.is_simulation:
                result = self.post_price(price_no_precision, info_contracts, task=task)
            else:
                log.info("Task :: {0} :: Simulation Post! ".format(task.task_name))

            # save the last price to compare
            global_manager['last_price'] = price_no_precision

            # save the last timestamp to compare
            global_manager['last_price_timestamp'] = datetime.datetime.now()

        if result:
            return result
        else:
            return save_pending_tx_receipt(None, task.task_name)


class PriceFeederTaskETH(PriceFeederTaskBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)


class PriceFeederTaskUSDT(PriceFeederTaskBase):

    def __init__(self, price_f_config, config_net, connection_net):

        super().__init__(price_f_config, config_net, connection_net)
