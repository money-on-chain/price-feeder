from config_parser import ConfigParser
from price_feeder.tasks import PriceFeederTaskMoC, PriceFeederTaskRIF, PriceFeederTaskETH, PriceFeederTaskUSDT


if __name__ == '__main__':

    config_parser = ConfigParser()

    app_mode = config_parser.config['networks'][config_parser.config_network]['app_mode']

    if app_mode == 'MoC':
        price_feeder_tasks = PriceFeederTaskMoC(
            config_parser.config,
            config_parser.config_network,
            config_parser.connection_network
        )
    elif app_mode == 'RIF':
        price_feeder_tasks = PriceFeederTaskRIF(
            config_parser.config,
            config_parser.config_network,
            config_parser.connection_network
        )
    elif app_mode == 'ETH':
        price_feeder_tasks = PriceFeederTaskETH(
            config_parser.config,
            config_parser.config_network,
            config_parser.connection_network
        )
    elif app_mode == 'USDT':
        price_feeder_tasks = PriceFeederTaskUSDT(
            config_parser.config,
            config_parser.config_network,
            config_parser.connection_network
        )
    else:
        raise Exception("App mode not recognize!")

    price_feeder_tasks.start_loop()
