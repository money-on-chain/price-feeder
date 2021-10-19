import os
import json
from optparse import OptionParser


class ConfigParser(object):

    @staticmethod
    def options_from_config(filename=None):
        """ Options from file config.json """

        if not filename:
            filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.json')

        with open(filename) as f:
            options = json.load(f)

        return options

    @staticmethod
    def options_to_settings(json_content, filename='settings.json'):
        """ Options to file settings.json """

        with open(filename, 'w') as f:
            json.dump(json_content, f, indent=4)

    def __init__(self,
                 connection_network='rskTesnetPublic',
                 config_network='mocTestnetAlpha',
                 options=None):

        self.connection_network = connection_network
        self.config_network = config_network
        if not options:
            self.config = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.json')
        else:
            self.config = options
        self.parse()

    def parse(self):

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
            self.config = json.loads(os.environ['APP_CONFIG'])
        else:
            if not options.config:
                # if there are no config try to read config.json from current folder
                config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
                if not os.path.isfile(config_path):
                    raise Exception("Please select path to config or env APP_CONFIG. "
                                    "Ex. /enviroments/moc-testnet/config.json "
                                    "Full Ex.:"
                                    "python app_run_price_feeder.py "
                                    "--connection_network=rskTestnetPublic "
                                    "--config_network=mocTestnet "
                                    "--config ./enviroments/moc-testnet/config.json"
                                    )
            else:
                config_path = options.config

            self.config = self.options_from_config(config_path)

        if 'APP_CONNECTION_NETWORK' in os.environ:
            self.connection_network = os.environ['APP_CONNECTION_NETWORK']
        else:
            if not options.connection_network:
                raise Exception("Please select connection network or env APP_CONNECTION_NETWORK. "
                                "Ex.: rskTesnetPublic. "
                                "Full Ex.:"
                                "python app_run_price_feeder.py "
                                "--connection_network=rskTestnetPublic "
                                "--config_network=mocTestnet "
                                "--config ./enviroments/moc-testnet/config.json")
            else:
                self.connection_network = options.connection_network

        if 'APP_CONFIG_NETWORK' in os.environ:
            self.config_network = os.environ['APP_CONFIG_NETWORK']
        else:
            if not options.config_network:
                raise Exception("Please select enviroment of your config or env APP_CONFIG_NETWORK. "
                                "Ex.: rdocTestnetAlpha"
                                "Full Ex.:"
                                "python app_run_price_feeder.py "
                                "--connection_network=rskTestnetPublic "
                                "--config_network=mocTestnet "
                                "--config ./enviroments/moc-testnet/config.json"
                                )
            else:
                self.config_network = options.config_network
