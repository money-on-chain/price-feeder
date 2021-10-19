from time import sleep
import signal
import functools
import uuid
from concurrent.futures import TimeoutError
import datetime
from multiprocessing import Manager

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
        self.task_name = task_name


class TasksManager:

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
                elif 'receipt' in task.result:
                    if 'id' in task.result['receipt']:
                        task.tx_receipt = task.result['receipt']['id']
                        task.tx_receipt_timestamp = task.result['receipt']['timestamp']
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
                future = pool.schedule(task.func, args=task.args, kwargs=task.kwargs, timeout=task.timeout)
                future.add_done_callback(functools.partial(self.on_task_done, task=task))

    def start_loop(self):

        log.info("Start Task jobs loop")
        global_manager = Manager().dict()

        with ProcessPool(max_workers=self.max_workers, max_tasks=self.max_tasks) as pool:
            try:
                while True:
                    if self.tasks:
                        for key in self.tasks:
                            self.schedule_task(pool, self.tasks[key], global_manager=global_manager)
                    sleep(1)
            except TerminateSignal:
                log.info("Terminal Signal received... Going to shutdown... stop pooling now!")
                #pool.stop()
                # wait to finish tasks ...
                pool.close()
                pool.join(timeout=self.timeout)

        log.info("End Task Jobs loop")


def test_task_1(task_id):
    print("Start task 1 id: {}".format(task_id))
    sleep(2)
    print("End task 1 id: {}".format(task_id))


def test_task_2(task_id):
    print("Start task 2 id: {}".format(task_id))
    sleep(10)
    print("End task 2 id: {}".format(task_id))


if __name__ == '__main__':
    jobs = TasksManager()
    jobs.add_task(test_task_1, args=[1])
    jobs.add_task(test_task_2, args=[5])
    jobs.start_loop()
