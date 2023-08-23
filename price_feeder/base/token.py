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
from web3 import Web3
from web3.types import BlockIdentifier
from decimal import Decimal

from .contracts import Contract


class ERC20Token(Contract):

    log = logging.getLogger()
    precision = 10 ** 18

    contract_abi = Contract.content_abi_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abi/ERC20Token.abi'))

    def __init__(self, connection_manager, contract_address=None, contract_abi=None, contract_bin=None):

        super().__init__(connection_manager,
                         contract_address=contract_address,
                         contract_abi=contract_abi,
                         contract_bin=contract_bin)

        # finally load the contract
        self.load_contract()

    def name(self):
        return self.sc.functions.name().call()

    def symbol(self):
        return self.sc.functions.symbol().call()

    def total_supply(self, formatted=True,
                     block_identifier: BlockIdentifier = 'latest'):

        total = self.sc.functions.totalSupply().call(block_identifier=block_identifier)
        if formatted:
            total = Web3.from_wei(total, 'ether')
        return total

    def balance_of(self, account_address, formatted=True,
                   block_identifier: BlockIdentifier = 'latest'):

        account_address = Web3.to_checksum_address(account_address)

        balance = self.sc.functions.balanceOf(account_address).call(
            block_identifier=block_identifier)
        if formatted:
            balance = Web3.from_wei(balance, 'ether')
        return balance
