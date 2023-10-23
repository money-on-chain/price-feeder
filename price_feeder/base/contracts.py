"""
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN PACKAGE
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

import json
import logging


class Contract(object):

    log = logging.getLogger()
    contract_address = None
    contract_abi = None
    contract_bin = None
    sc = None

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        self.connection_manager = connection_manager

        # Contract address
        if contract_address:
            self.contract_address = contract_address

        # Contract abi
        if contract_abi:
            self.contract_abi = contract_abi

        # Contract bin
        if contract_bin:
            self.contract_bin = contract_bin

    def address(self):
        return self.sc.address

    @staticmethod
    def content_abi_file(abi_file):

        with open(abi_file) as f:
            abi = json.load(f)

        return abi

    @staticmethod
    def content_bin_file(bin_file):

        with open(bin_file) as f:
            content_bin = f.read()

        return content_bin

    def load_abi_file(self, abi_file):

        self.contract_abi = self.content_abi_file(abi_file)

    def load_bin_file(self, bin_file):

        self.contract_bin = self.content_bin_file(bin_file)

    def load_contract_from_address(self, contract_address):

        if not self.contract_abi:
            raise Exception("Error. First you need to load data abi")

        self.sc = self.connection_manager.load_contract(self.contract_abi, contract_address)

        return self.sc

    def load_contract(self):

        if not self.contract_abi:
            raise Exception("Error. First you need to load data abi")

        if not self.contract_address:
            raise Exception("Error. You need contract address")

        self.sc = self.connection_manager.load_contract(self.contract_abi, self.contract_address)

        return self.sc

    def logs_from(self, events_functions, from_block, to_block, block_steps=2880):

        logs = self.connection_manager.logs_from(self.sc,
                                                 events_functions,
                                                 from_block,
                                                 to_block,
                                                 block_steps=block_steps)

        return logs

    @property
    def events(self):

        return self.sc.events

