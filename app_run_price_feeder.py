import os
import json


from price_feeder.tasks import PriceFeederTaskMoC, \
    PriceFeederTaskRIF, \
    PriceFeederTaskETH, \
    PriceFeederTaskUSDT, \
    PriceFeederTaskBNB, \
    PriceFeederTaskARS, \
    PriceFeederTaskMXN


def options_from_config(filename=None):
    """ Options from file config.json """

    if not filename:
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

    with open(filename) as f:
        options = json.load(f)

    return options


if __name__ == '__main__':

    config = options_from_config()

    # override config default
    if 'APP_CONFIG' in os.environ:
        config = json.loads(os.environ['APP_CONFIG'])

    # override connection uri from env
    if 'APP_CONNECTION_URI' in os.environ:
        config['uri'] = os.environ['APP_CONNECTION_URI']

    app_mode = config['app_mode']

    if app_mode == 'MoC':
        price_feeder_tasks = PriceFeederTaskMoC(config)
    elif app_mode == 'RIF':
        price_feeder_tasks = PriceFeederTaskRIF(config)
    elif app_mode == 'ETH':
        price_feeder_tasks = PriceFeederTaskETH(config)
    elif app_mode == 'USDT':
        price_feeder_tasks = PriceFeederTaskUSDT(config)
    elif app_mode == 'BNB':
        price_feeder_tasks = PriceFeederTaskBNB(config)
    elif app_mode == 'ARS':
        price_feeder_tasks = PriceFeederTaskARS(config)
    elif app_mode == 'MXN':
        price_feeder_tasks = PriceFeederTaskMXN(config)
    else:
        raise Exception("App mode not recognize!")

    price_feeder_tasks.start_loop()
