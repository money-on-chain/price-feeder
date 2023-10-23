"""
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 THIS IS A PART OF MONEY ON CHAIN PACKAGE
 by Martin Mulone (martin.mulone@moneyonchain.com)

"""

import os
import logging
from web3.types import BlockIdentifier
from web3 import Web3

from .base.contracts import Contract


class MoCMedianizer(Contract):

    log = logging.getLogger()
    precision = 10 ** 18

    contract_name = 'MoCMedianizer'
    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/MoCMedianizer.abi'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def poke(
            self,
            *args,
            **kwargs):

        tx_hash = self.connection_manager.send_function_transaction(
            self.sc.functions.poke,
            *args,
            **kwargs
        )

        return tx_hash

    def peek(self, formatted: bool = True, block_identifier: BlockIdentifier = 'latest'):

        result = self.sc.functions.peek().call(block_identifier=block_identifier)

        price = Web3.to_int(result[0])

        if formatted:
            price = Web3.from_wei(price, 'ether')

        return price, result[1]


class PriceFeed(Contract):

    log = logging.getLogger()
    precision = 10 ** 18

    contract_name = 'PriceFeed'
    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/PriceFeed.abi'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def post(
            self,
            *args,
            **kwargs):

        tx_hash = self.connection_manager.send_function_transaction(
            self.sc.functions.post,
            *args,
            **kwargs
        )

        return tx_hash


class MoCState(Contract):

    log = logging.getLogger()
    precision = 10 ** 18

    contract_name = 'MoCState'
    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/moc/MoCState.abi'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def price_moving_average(self,
                             formatted: bool = True,
                             block_identifier: BlockIdentifier = 'latest'):

        result = self.sc.functions.getBitcoinMovingAverage().call(
            block_identifier=block_identifier)

        if formatted:
            result = Web3.from_wei(result, 'ether')

        return result


class MoCStateRRC20(MoCState):

    log = logging.getLogger()
    precision = 10 ** 18

    contract_name = 'MoCState'
    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/rrc20/MoCState.abi'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def price_moving_average(self,
                             formatted: bool = True,
                             block_identifier: BlockIdentifier = 'latest'):
        result = self.sc.functions.getExponentalMovingAverage().call(block_identifier=block_identifier)

        if formatted:
            result = Web3.from_wei(result, 'ether')

        return result
