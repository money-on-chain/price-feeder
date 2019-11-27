import datetime

# local imports
from price_engines import PriceEngines, PriceEngineBase


class PriceEngineTest1(PriceEngineBase):
    name = "test_1"
    description = "Test 1"
    uri = "http://api.pricefetcher.com/BTCUSD"
    convert = "BTC_USD"

    def get_price(self, session):

        d_price_info = dict()
        d_price_info['price'] = 7250.10
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest2(PriceEngineBase):
    name = "test_2"
    description = "Test 2"
    uri = "http://api.pricefetcher.com/BTCUSD"
    convert = "BTC_USD"

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7258.32
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest3(PriceEngineBase):
    name = "test_3"
    description = "Test 3"
    uri = "http://api.pricefetcher.com/BTCUSD"
    convert = "BTC_USD"

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7283.81
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest4(PriceEngineBase):
    name = "test_4"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7286.25
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest5(PriceEngineBase):
    name = "test_5"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7250.10
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest6(PriceEngineBase):
    name = "test_6"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7283.81
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest7(PriceEngineBase):
    name = "test_7"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7286.25
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest8(PriceEngineBase):
    name = "test_8"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7984.15
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest9(PriceEngineBase):
    name = "test_9"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7250.1
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest10(PriceEngineBase):
    name = "test_10"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7283.81
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest11(PriceEngineBase):
    name = "test_11"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7286.25
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest12(PriceEngineBase):
    name = "test_12"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):

        return None, "Error"


class PriceEngineTest13(PriceEngineBase):
    name = "test_13"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 8000
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest14(PriceEngineBase):
    name = "test_14"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7000
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest15(PriceEngineBase):
    name = "test_15"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7000
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


class PriceEngineTest16(PriceEngineBase):
    name = "test_16"
    description = ""
    uri = ""
    convert = ""

    def get_price(self, session):
        d_price_info = dict()
        d_price_info['price'] = 7000
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()

        return d_price_info, None


engines_names_1 = {
    "test_1": PriceEngineTest1,
    "test_2": PriceEngineTest2,
    "test_3": PriceEngineTest3,
    "test_4": PriceEngineTest4
}

engines_names_2 = {
    "test_5": PriceEngineTest5,
    "test_6": PriceEngineTest6,
    "test_7": PriceEngineTest7,
    "test_8": PriceEngineTest8
}

engines_names_3 = {
    "test_9": PriceEngineTest9,
    "test_10": PriceEngineTest10,
    "test_11": PriceEngineTest11,
    "test_12": PriceEngineTest12
}

engines_names_4 = {
    "test_13": PriceEngineTest13,
    "test_14": PriceEngineTest14,
    "test_15": PriceEngineTest15,
    "test_16": PriceEngineTest16
}


if __name__ == '__main__':

    price_options = [
        {"name": "test_1", "ponderation": 0.1605, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_2", "ponderation": 0.2138, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_3", "ponderation": 0.2782, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_4", "ponderation": 0.3475, "min_volume":  0.0, "max_delay": 0}
    ]

    pr_engine = PriceEngines(price_options, engines_names=engines_names_1)
    w_prices = pr_engine.get_weighted()
    w_median = pr_engine.get_weighted_median(w_prices)

    md_header = '''
| Name        | Price        | Ponderation    | Price Ponderated  | Original Ponderation |
| :--------:  | :----------- | ------------   | ----------------- |--------------------- |
    '''
    print(md_header)

    for w_price in w_prices:
        print("| {name} |  {price} | {ponderation} | {ponderated} | {o_ponderation} |".format(
            name=w_price['name'],
            price=w_price['price'],
            ponderation=format(w_price['price_ponderation'], '.3f'),
            ponderated=format(w_price['price_ponderated'], '.3f'),
            o_ponderation=w_price['ponderation']))
    print("")
    print("**Weighted median:** {0}".format(w_median))
    print("")

    price_options = [
        {"name": "test_5", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_6", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_7", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_8", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0}
    ]

    pr_engine = PriceEngines(price_options, engines_names=engines_names_2)
    w_prices = pr_engine.get_weighted()
    w_median = pr_engine.get_weighted_median(w_prices)

    md_header = '''
| Name        | Price        | Ponderation    | Price Ponderated  | Original Ponderation |
| :--------:  | :----------- | ------------   | ----------------- |--------------------- |
        '''
    print(md_header)

    for w_price in w_prices:
        print("| {name} |  {price} | {ponderation} | {ponderated} | {o_ponderation} |".format(
            name=w_price['name'],
            price=w_price['price'],
            ponderation=format(w_price['price_ponderation'], '.3f'),
            ponderated=format(w_price['price_ponderated'], '.3f'),
            o_ponderation=w_price['ponderation']))
    print("")
    print("**Weighted median:** {0}".format(w_median))
    print("")

    price_options = [
        {"name": "test_9", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_10", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_11", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_12", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0}
    ]

    pr_engine = PriceEngines(price_options, engines_names=engines_names_3)
    w_prices = pr_engine.get_weighted()
    w_median = pr_engine.get_weighted_median(w_prices)

    md_header = '''
| Name        | Price        | Ponderation    | Price Ponderated  | Original Ponderation |
| :--------:  | :----------- | ------------   | ----------------- |--------------------- |
        '''
    print(md_header)

    for w_price in w_prices:
        print("| {name} |  {price} | {ponderation} | {ponderated} | {o_ponderation} |".format(
            name=w_price['name'],
            price=w_price['price'],
            ponderation=format(w_price['price_ponderation'], '.3f'),
            ponderated=format(w_price['price_ponderated'], '.3f'),
            o_ponderation=w_price['ponderation']))
    print("")
    print("**Weighted median:** {0}".format(w_median))
    print("")

    price_options = [
        {"name": "test_13", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_14", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_15", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_16", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0}
    ]

    pr_engine = PriceEngines(price_options, engines_names=engines_names_3)
    w_prices = pr_engine.get_weighted()
    w_median = pr_engine.get_weighted_median(w_prices)

    md_header = '''
    | Name        | Price        | Ponderation    | Price Ponderated  | Original Ponderation |
    | :--------:  | :----------- | ------------   | ----------------- |--------------------- |
            '''
    print(md_header)

    for w_price in w_prices:
        print("| {name} |  {price} | {ponderation} | {ponderated} | {o_ponderation} |".format(
            name=w_price['name'],
            price=w_price['price'],
            ponderation=format(w_price['price_ponderation'], '.3f'),
            ponderated=format(w_price['price_ponderated'], '.3f'),
            o_ponderation=w_price['ponderation']))
    print("")
    print("**Weighted median:** {0}".format(w_median))
    print("")
