from time import sleep
import signal
import functools
import uuid
from concurrent.futures import TimeoutError
import datetime
from multiprocessing import Manager
from web3 import Web3, exceptions
from functools import wraps


from pebble import ProcessPool, sighandler, ProcessExpired, ThreadPool

from .logger import log
from .utils import aws_put_metric_heart_beat


class TerminateSignal(Exception):
    """Traceback wrapper for exceptions in remote process.
    Exception.__cause__ requires a BaseException subclass.
    """
    pass


@sighandler((signal.SIGINT, signal.SIGTERM))
def signal_handler(signum, frame):
    log.info("Termination request received!")
    raise TerminateSignal


class Task:
    def __init__(self, func, args=None, kwargs=None, wait=1, timeout=180, task_name='Task N'):
        self.func = func
        if args:
            self.args = args
        else:
            self.args = list()
        if kwargs:
            self.kwargs = kwargs
        else:
            self.kwargs = dict()
        self.wait = wait
        self.timeout = timeout
        self.running = False
        self.result = None
        self.shutdown = False
        self.last_run = datetime.datetime.now()
        self.tx_receipt = None
        self.tx_receipt_timestamp = None
        self.pending_transactions = None
        self.task_name = task_name


class TransactionsTasksManager:

    def __init__(self):
        self.tasks = dict()
        self.max_workers = 1
        self.max_tasks = 1
        self.timeout = 180

    def add_task(self, func, args=None, kwargs=None, wait=1, timeout=180, tid=None, task_name='Task N'):

        if not tid:
            tid = uuid.uuid4()

        task = Task(func, args=args, kwargs=kwargs, wait=wait, timeout=timeout, task_name=task_name)
        self.tasks[tid] = task

    def on_task_done(self, future, task=None):

        try:
            task.result = future.result()  # blocks until results are ready
            if isinstance(task.result, dict):
                if 'shutdown' in task.result:
                    if task.result['shutdown']:
                        task.shutdown = True
                elif 'pending_transactions' in task.result:
                    task.pending_transactions = task.result['pending_transactions']
                elif 'receipt' in task.result:
                    if 'id' in task.result['receipt']:
                        task.tx_receipt = task.result['receipt']['id']
                        task.tx_receipt_timestamp = task.result['receipt']['timestamp']
                        task.is_replacement = task.result['receipt'].get('is_replacement', False)
                        task.price_oracle = task.result['receipt'].get('price_oracle', '')
                        task.price_last_time = task.result['receipt'].get('price_last_time', '')
                        task.price_new = task.result['receipt'].get('price_new', '')
                        task.variation_oracle = task.result['receipt'].get('variation_oracle', '')
                        task.variation_last_time = task.result['receipt'].get('variation_last_time', '')
                        task.gas_price = task.result['receipt'].get('gas_price', '')
                        task.gas_price_replacement = task.result['receipt'].get('gas_price_replacement', '')
                        task.nonce = task.result['receipt'].get('nonce', '')
                        task.nonce_replacement = task.result['receipt'].get('nonce_replacement', '')


        except TimeoutError as e:
            log.info("Function took longer than %d seconds. Task going to cancel!" % e.args[1])
            aws_put_metric_heart_beat(1)
            future.cancel()
        except ProcessExpired as e:
            log.info("%s. Exit code: %d" % (e, e.exitcode))
            aws_put_metric_heart_beat(1)
            future.cancel()
        except Exception as e:
            log.info("Function raised %s" % e)
            log.info(e, exc_info=True)
            aws_put_metric_heart_beat(1)
            future.cancel()

        task.last_run = datetime.datetime.now()
        task.running = False

    def schedule_task(self, pool, task, global_manager=None):

        if not task.running:
            # shutdown task manager!
            if task.shutdown:
                raise TerminateSignal
            if task.last_run + datetime.timedelta(seconds=task.wait) <= datetime.datetime.now():
                task.running = True
                # pass task object as vars to run funtion
                task.kwargs["task"] = task
                task.kwargs["global_manager"] = global_manager
                future = pool.schedule(task.func, args=task.args, kwargs=task.kwargs)
                future.add_done_callback(functools.partial(self.on_task_done, task=task))

    def start_loop(self):

        log.info("Start Task jobs loop")
        global_manager = Manager().dict()

        with ThreadPool(max_workers=self.max_workers, max_tasks=self.max_tasks) as pool:
            try:
                while True:
                    if self.tasks:
                        for key in self.tasks:
                            self.schedule_task(pool, self.tasks[key], global_manager=global_manager)
            except TerminateSignal:
                log.info("Terminal Signal received... Going to shutdown... stop pooling now!")
                #pool.stop()
                # wait to finish tasks ...
                pool.close()
                pool.join(timeout=self.timeout)

        log.info("End Task Jobs loop")


def on_pending_transactions(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        pending_txs = self.pending_transactions(method_kwargs['task'])
        task_result = dict()
        task_result['pending_transactions'] = pending_txs
        method_kwargs['task_result'] = task_result
        method_result = method(self, *method_args, **method_kwargs)
        return method_result
    return _impl


class PendingTransactionsTasksManager(TransactionsTasksManager):

    def __init__(self,
                 config,
                 connection_helper,
                 contracts_loaded
                 ):

        TransactionsTasksManager.__init__(self)

        self.config = config
        self.connection_helper = connection_helper
        self.contracts_loaded = contracts_loaded

    def pending_queue_is_full(self, account_index=0):

        web3 = self.connection_helper.connection_manager.web3

        # get first account
        account_address = self.connection_helper.connection_manager.accounts[account_index].address

        nonce = web3.eth.get_transaction_count(account_address, 'pending')
        last_used_nonce = web3.eth.get_transaction_count(account_address)

        # A limit of pending on blockchain
        if nonce >= last_used_nonce + self.config['max_pending_txs']:
            #log.info('Cannot create more transactions for {} as the node queue will be full [{}, {}]'.format(
            #    account_address, nonce, last_used_nonce))
            return True

        return False

    @staticmethod
    def remove_nonce_pending_transactions(pending_transactions, nonce):

        count = 0
        for tx in pending_transactions:
            if tx['nonce'] == nonce:
                pending_transactions.remove(tx)
                count += 1

        return count

    def pending_transactions(self, task):
        """ Wait to pending receipt get confirmed"""

        web3 = self.connection_helper.connection_manager.web3

        if not task.pending_transactions:
            task.pending_transactions = list()
        else:

            for tx in task.pending_transactions:
                # log.info("DEBUG 5>>>")
                # log.info(tx)

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
                            Web3.to_hex(tx['hash']),
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

                    #task.pending_transactions.remove(tx)
                    self.remove_nonce_pending_transactions(task.pending_transactions, tx['nonce'])

                    continue

                try:
                    tx_rcp = web3.eth.get_transaction_receipt(tx['hash'])
                except exceptions.TransactionNotFound:

                    # 1. STATUS: Pending tx

                    # timeout and permit to send again transaction
                    elapsed = datetime.datetime.now() - tx['timestamp']

                    if tx['is_replacement']:
                        timeout_waiting = self.config['timeout_pending_replace_tx']
                        label_timeout = 'Timeout TX Replacement!'
                    else:
                        timeout_waiting = self.config['timeout_pending_tx']
                        label_timeout = 'Timeout TX!'

                    timeout = datetime.timedelta(seconds=timeout_waiting)

                    if elapsed > timeout:

                        log.error("Task :: {0} :: {1} [{2}]".format(
                            task.task_name, label_timeout, Web3.from_wei(tx['hash'])))
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
                                Web3.to_hex(tx['hash']),
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
                            Web3.to_hex(tx['hash']),
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

                    if tx['is_replacement']:
                        timeout_waiting = self.config['timeout_pending_replace_tx']
                        label_timeout = 'Reverted TX Replacement!'
                    else:
                        timeout_waiting = self.config['timeout_pending_tx']
                        label_timeout = 'Reverted TX!'

                    timeout = datetime.timedelta(seconds=timeout_waiting)

                    log.error("Task :: {0} :: {1} [{2}] Elapsed: [{3}] Timeout: [{4}]".format(
                        task.task_name, label_timeout, Web3.from_wei(tx['hash']), elapsed.seconds, timeout))

                    task.pending_transactions.remove(tx)

        return task.pending_transactions


def test_task_1(task_id):
    print("Start task 1 id: {}".format(task_id))
    sleep(2)
    print("End task 1 id: {}".format(task_id))


def test_task_2(task_id):
    print("Start task 2 id: {}".format(task_id))
    sleep(10)
    print("End task 2 id: {}".format(task_id))


if __name__ == '__main__':
    jobs = TransactionsTasksManager()
    jobs.add_task(test_task_1, args=[1])
    jobs.add_task(test_task_2, args=[5])
    jobs.start_loop()
