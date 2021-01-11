"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
    software and other kinds of works.

  Martin Mulone @2020 Moneyonchain
"""

import requests, engines, click
import numpy as np
from statistics import median, mean
from tabulate import tabulate
import decimal



def weighted_median(values, weights):
    ''' compute the weighted median of values list. The
weighted median is computed as follows:
    1- sort both lists (values and weights) based on values.
    2- select the 0.5 point from the weights and return the corresponding values as results
    e.g. values = [1, 3, 0] and weights=[0.1, 0.3, 0.6] assuming weights are probabilities.
    sorted values = [0, 1, 3] and corresponding sorted weights = [0.6,     0.1, 0.3] the 0.5 point on
    weight corresponds to the first item which is 0. so the weighted     median is 0.'''

    # convert the weights into probabilities
    sum_weights = sum(weights)
    weights = np.array([(w*1.0)/sum_weights for w in weights])
    # sort values and weights based on values
    values = np.array(values)
    sorted_indices = np.argsort(values)
    values_sorted  = values[sorted_indices]
    weights_sorted = weights[sorted_indices]
    # select the median point
    it = np.nditer(weights_sorted, flags=['f_index'])
    accumulative_probability = 0
    median_index = -1
    while not it.finished:
        accumulative_probability += it[0]
        if accumulative_probability > 0.5:
            median_index = it.index
            return values_sorted[median_index]
        elif accumulative_probability == 0.5:
            median_index = it.index
            it.iternext()
            next_median_index = it.index
            return np.mean(values_sorted[[median_index, next_median_index]])
        it.iternext()

    return values_sorted[median_index]


class LogMeta(object):

    @staticmethod
    def info(msg):
        print("INFO: {0}".format(msg))

    @staticmethod
    def error(msg):
        print("ERROR: {0}".format(msg))


class PriceEngines(object):

    def __init__(self, price_options, log=None, engines_names=None, app_mode='MoC'):
        self.price_options = price_options
        self.engines = list()

        # log settings
        if not log:
            log = LogMeta()
        self.log = log

        # engine names
        if not engines_names:
            if app_mode == 'MoC':
                engines_names = engines.pairs['BTC_USD']
            elif app_mode == 'RIF':
                engines_names = engines.pairs['RIF_BTC']
            else:
                raise Exception("Not valid app mode")

        self.engines_names = engines_names

        self.add_engines()

    def add_engines(self):

        price_engines = self.price_options
        for price_engine in price_engines:
            engine_name = price_engine["name"]

            if engine_name not in self.engines_names:
                raise Exception("The engine price name not in the avalaible list")

            engine = self.engines_names.get(engine_name)
            i_engine = engine(self.log)

            d_engine = dict()
            d_engine["engine"] = i_engine
            d_engine["name"]   = engine_name

            for key in ["ponderation", "min_volume", "max_delay"]:
                d_engine[key] = price_engine[key]

            self.engines.append(d_engine)

    def fetch_prices(self, session=None):

        # create persistent HTTP connection
        if not session:
            session = requests.Session()

        prices = list()
        for engine in self.engines:
            d_price, err_msg = engine["engine"].get_price(session)
            if d_price:

                i_price = dict()

                for key in ["name", "ponderation", "min_volume", "max_delay"]:
                    i_price[key] = engine[key]

                for key in ["price", "volume", "timestamp"]:
                    i_price[key] = d_price[key]

                if i_price["min_volume"] > 0:
                    # the evalution of volume is on
                    if not i_price['volume'] > i_price["min_volume"]:
                        # is not added to the price list
                        self.log.warning("Not added to the list because is not at to the desire volume: %s" %
                                         i_price['name'])
                        continue

                prices.append(i_price)

        return prices

    def get_mean(self, session=None):

        f_prices = self.fetch_prices(session=session)
        prices = list()
        for f_price in f_prices:
            price = f_price["price"]
            prices.append(price)

        return mean(prices)

    def get_weighted(self, session=None, btc_price_assign=None):

        f_prices = self.fetch_prices(session=session)

        if len(f_prices) < 1:
            raise Exception("At least we need 1 price sources.")

        # The sum of the weight must not exceed 1
        total = sum([ pr["ponderation"] for pr in f_prices])
        for pr in f_prices:
            pr["price_ponderated"] = pr["price"] * pr["ponderation"]
            pr["price_ponderation"] = pr["ponderation"] / total

        self.report_exchanges(f_prices, btc_price_assign=btc_price_assign)

        return f_prices

    def report_exchanges(self, ex_prices, btc_price_assign=None):

        rep_titles = ['Name', 'Price', 'Ponderation', 'Price Ponderated', 'Price ponderation']
        d_table = []
        for ex_price in ex_prices:
            ex_row = list()
            ex_row.append(ex_price['name'])
            if btc_price_assign:
                ex_row.append(decimal.Decimal(ex_price['price']) * btc_price_assign)
            else:
                ex_row.append(ex_price['price'])
            ex_row.append(ex_price['ponderation'])
            if btc_price_assign:
                ex_row.append(decimal.Decimal(ex_price['price_ponderated']) * btc_price_assign)
            else:
                ex_row.append(ex_price['price_ponderated'])
            ex_row.append(ex_price['price_ponderation'])
            d_table.append(ex_row)

        # order table by price
        o_table = sorted(d_table, key=lambda k: k[1])

        self.log.info("")
        self.log.info("\n%s" % tabulate(o_table, headers=rep_titles, tablefmt="pipe"))
        self.log.info("")

    @staticmethod
    def get_weighted_median(fetch_weighted_prices):

        l_prices = list()
        l_weights = list()

        for p_price in fetch_weighted_prices:
            l_prices.append(p_price['price'])
            l_weights.append(p_price['price_ponderation'])

        w_median = weighted_median(l_prices, l_weights)
        return w_median

    def prices_weighted_median(self, btc_price_assign=None):

        w_prices = self.get_weighted(btc_price_assign=btc_price_assign)
        w_median = self.get_weighted_median(w_prices)
        return w_median


if __name__ == '__main__':

    session = requests.Session()

    display_table = []
    titles = ['Pair', 'Exchange', 'Price', 'Volume', 'Timestamp']

    for pair, d_engines in engines.pairs.items():
        with click.progressbar(d_engines.items(), label=pair) as bar:
            for name, Engine in bar:
                engine = Engine(LogMeta())
                d_price, foo = engine.get_price(session)
                d_row = d_price if d_price else  {'price': 'Error', 'volume': 'Error', 'timestamp': 'Error'}
                for key in ['convert', 'description']:
                    d_row[key] = getattr(engine, key)
                l_row = []
                for key in ['convert', 'description', 'price', 'volume', 'timestamp']:
                    l_row.append(d_row[key])
                display_table.append(l_row)


    print()
    print('Test of all engines')
    print('==== == === =======')
    print()
    print(tabulate(display_table, headers=titles, tablefmt="pipe"))
    print()

    print()
    print('Weighted Median Test')
    print('======== ====== ====')
    print()

    price_options_test = [
        {"name": "bitfinex_rif", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "bithumbpro_rif", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "kucoin_rif", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "coinbene_rif", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0}
    ]

    btc_price = 9050

    pr_engine = PriceEngines(price_options_test, app_mode='RIF')
    we_prices = pr_engine.get_weighted()
    we_median = pr_engine.get_weighted_median(we_prices)

    titles = ['Name', 'Price', 'Ponderation', 'Original Ponderation']
    display_table = []
    for we_price in we_prices:
        row = []
        row.append(we_price['name'])
        row.append(we_price['price'] * btc_price)
        row.append(we_price['price_ponderation'])
        row.append(we_price['ponderation'])
        display_table.append(row)

    print("")
    print(tabulate(display_table, headers=titles, tablefmt="pipe"))
    print("")
    print("**Weighted median:** {0}".format(we_median * btc_price))
    print("")

    price_options_test = [
        {"name": "binance", "ponderation": 1.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "bitstamp", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "coinbase", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "bitfinex", "ponderation": 0, "min_volume": 0.0, "max_delay": 0}
    ]

    pr_engine = PriceEngines(price_options_test, app_mode='MoC')
    we_prices = pr_engine.get_weighted()
    we_median = pr_engine.get_weighted_median(we_prices)

    titles = ['Name', 'Price', 'Ponderation', 'Original Ponderation']
    display_table = []
    for we_price in we_prices:
        row = []
        row.append(we_price['name'])
        row.append(we_price['price'])
        row.append(we_price['price_ponderation'])
        row.append(we_price['ponderation'])
        display_table.append(row)

    print("")
    print(tabulate(display_table, headers=titles, tablefmt="pipe"))
    print("")
    print("**Weighted median:** {0}".format(we_median ))
    print("")