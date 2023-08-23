import datetime
from web3 import Web3, exceptions
from functools import wraps

from .logger import log
from .utils import aws_put_metric_heart_beat


def on_pending_transactions(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        pending_txs = self.pending_transactions(method_kwargs['task'])
        task_result = dict()
        task_result['pending_transactions'] = pending_txs
        method_kwargs['task_result'] = task_result
        method_output = method(self, *method_args, **method_kwargs)
        return method_output
    return _impl


class PendingTransactionsTasksManager(TransactionsTasksManager):

    def __init__(self,
                 options,
                 connection_helper,
                 contracts_loaded
                 ):
        self.options = options
        self.connection_helper = connection_helper
        self.contracts_loaded = contracts_loaded

    def pending_queue_is_full(self, account_index=0):

        web3 = self.connection_helper.connection_manager.web3

        # get first account
        account_address = self.connection_helper.connection_manager.accounts[account_index].address

        nonce = web3.eth.get_transaction_count(account_address, 'pending')
        last_used_nonce = web3.eth.get_transaction_count(account_address)

        # A limit of pending on blockchain
        if nonce >= last_used_nonce + 1:
            log.info('Cannot create more transactions for {} as the node queue will be full [{}, {}]'.format(
                account_address, nonce, last_used_nonce))
            return True

        return False

    def pending_transactions(self, task):
        """ Wait to pending receipt get confirmed"""

        web3 = self.connection_helper.connection_manager.web3
        timeout_waiting = 180

        if not task.pending_transactions:
            task.pending_transactions = list()
        else:

            for tx in task.pending_transactions:
                log.info("DEBUG 5>>>")
                log.info(tx)

                try:
                    web3.eth.get_transaction(tx['hash'])
                except exceptions.TransactionNotFound:

                    # 4. STATUS: Dropped Tx

                    # Transaction not exist anymore or dropped, permit to send new tx
                    elapsed = datetime.datetime.now() - tx['timestamp']

                    if tx['is_replacement']:
                        action_label = 'Task :: {0} :: TX Replacement Dropped.'.format(task.task_name)
                    else:
                        action_label = 'Task :: {0} :: TX Dropped.'.format(task.task_name)

                    log.info(
                        "{0}"
                        " Hash: [{1}] "
                        " Price Oracle: [{2}] "
                        " Price Last Time: [{3}] "
                        " Price New: [{4}] "
                        " Variation Oracle: [{5}] "
                        " Variation Last Time: [{6}] "
                        " Gas Price: [{7}] "
                        " Nonce: [{8}] "
                        " Elapsed: [{9}]".format(
                            action_label,
                            tx['hash'],
                            tx['price_oracle'],
                            tx['price_last_time'],
                            tx['price_new'],
                            tx['variation_oracle'],
                            tx['variation_last_time'],
                            Web3.from_wei(tx['gas_price'], 'gwei'),
                            tx['nonce'],
                            elapsed.seconds
                        )
                    )

                    task.pending_transactions.remove(tx)

                    continue

                try:
                    tx_rcp = web3.eth.get_transaction_receipt(tx['hash'])
                except exceptions.TransactionNotFound:

                    # 1. STATUS: Pending tx

                    # timeout and permit to send again transaction
                    elapsed = datetime.datetime.now() - tx['timestamp']
                    timeout = datetime.timedelta(seconds=timeout_waiting)

                    if elapsed > timeout:
                        log.error("Task :: {0} :: Timeout tx! [{1}]".format(task.task_name, tx['hash']))
                        task.pending_transactions.remove(tx)

                    else:

                        if tx['is_replacement']:
                            action_label = 'Task :: {0} :: TX Replacement Pending.'.format(task.task_name)
                        else:
                            action_label = 'Task :: {0} :: TX Pending.'.format(task.task_name)

                        log.info(
                            "{0}"
                            " Hash: [{1}] "
                            " Price Oracle: [{2}] "
                            " Price Last Time: [{3}] "
                            " Price New: [{4}] "
                            " Variation Oracle: [{5}] "
                            " Variation Last Time: [{6}] "
                            " Gas Price: [{7}] "
                            " Nonce: [{8}] "
                            " Elapsed: [{9}]".format(
                                action_label,
                                tx['hash'],
                                tx['price_oracle'],
                                tx['price_last_time'],
                                tx['price_new'],
                                tx['variation_oracle'],
                                tx['variation_last_time'],
                                Web3.to_wei(tx['gas_price'], 'ether'),
                                tx['nonce'],
                                elapsed.seconds
                            )
                        )

                    continue

                # 2. STATUS: Confirmed status
                if tx_rcp['status'] > 0:

                    elapsed = datetime.datetime.now() - tx['timestamp']

                    if tx['is_replacement']:
                        action_label = 'Task :: {0} :: TX Replacement Confirmed.'.format(task.task_name)
                    else:
                        action_label = 'Task :: {0} :: TX Confirmed.'.format(task.task_name)

                    log.info(
                        "{0}"
                        " Hash: [{1}] "
                        " Price Oracle: [{2}] "
                        " Price Last Time: [{3}] "
                        " Price New: [{4}] "
                        " Variation Oracle: [{5}] "
                        " Variation Last Time: [{6}] "
                        " Gas Price: [{7}] "
                        " Nonce: [{8}] "
                        " Elapsed: [{9}]".format(
                            action_label,
                            tx['hash'],
                            tx['price_oracle'],
                            tx['price_last_time'],
                            tx['price_new'],
                            tx['variation_oracle'],
                            tx['variation_last_time'],
                            Web3.to_wei(tx['gas_price'], 'ether'),
                            tx['nonce'],
                            elapsed.seconds
                        )
                    )

                    task.pending_transactions.remove(tx)

                # 3. STATUS: Reverted status
                else:

                    elapsed = datetime.datetime.now() - tx['timestamp']
                    timeout = datetime.timedelta(seconds=timeout_waiting)

                    log.error("Task :: {0} :: Reverted tx! [{1}] Elapsed: [{2}] Timeout: [{3}]".format(
                        task.task_name, tx['hash'], elapsed.seconds, timeout))

                    task.pending_transactions.remove(tx)

        return task.pending_transactions

