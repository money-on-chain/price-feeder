import os
import subprocess

import logging
import logging.config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger('default')


def add_custom_network(connection_net):
    """ add custom network"""

    if connection_net.startswith("https") or connection_net.startswith("http"):
        a_connection = connection_net.split(',')
        host = a_connection[0]
        chain_id = a_connection[1]

        network_group_name = "RskNetwork"
        network_name = 'rskCustomNetwork'
        network_explorer = 'https://blockscout.com/rsk/mainnet/api'

        subprocess.run(["brownie", "networks", "add",
                        network_group_name,
                        network_name,
                        "host={}".format(host),
                        "chainid={}".format(chain_id),
                        "explorer={}".format(network_explorer),
                        "timeout=180"])


if __name__ == '__main__':

    if 'APP_CONNECTION_NETWORK' in os.environ:
        log.info("Adding custom network ...")
        connection_network = os.environ['APP_CONNECTION_NETWORK']
        add_custom_network(connection_network)
