from .network import ConnectionManager


class ConnectionHelperBase(object):

    precision = 10 ** 18

    def __init__(self, config):
        self.config = config
        self.config_uri = config["uri"]
        self.chain_id = config["chain_id"]
        self.connection_manager = self.connect_node()

    def connect_node(self):

        return ConnectionManager(uris=self.config_uri, chain_id=self.chain_id)
