import datetime
from tabulate import tabulate

# local imports
from price_engines import PriceEngines
from engines.base import Base


def make_fake_engine(name_, price_, error_=False):

    class PriceEngineFake(Base):

        name        = name_
        description = name_
        uri         = "http://api.fake-uri.com/BTCUSD"
        convert     = "BTC_USD"

        def get_price(self, session):

            d_price_info = dict()
            d_price_info['price'] = price_
            d_price_info['volume'] = 0.0
            d_price_info['timestamp'] = datetime.datetime.now()

            if error_:
                return None, "Error"
            return d_price_info, None

    return PriceEngineFake


PriceEngineTest1  = make_fake_engine("test_1",  7250.10)
PriceEngineTest2  = make_fake_engine("test_2",  7258.32)
PriceEngineTest3  = make_fake_engine("test_3",  7283.81)
PriceEngineTest4  = make_fake_engine("test_4",  7286.25)
PriceEngineTest5  = make_fake_engine("test_5",  7250.10)
PriceEngineTest6  = make_fake_engine("test_6",  7283.81)
PriceEngineTest7  = make_fake_engine("test_7",  7286.25)
PriceEngineTest8  = make_fake_engine("test_8",  7984.15)
PriceEngineTest9  = make_fake_engine("test_9",  7250.10)
PriceEngineTest10 = make_fake_engine("test_10", 7283.81)
PriceEngineTest11 = make_fake_engine("test_11", 7286.25)
PriceEngineTest12 = make_fake_engine("test_12", 7286.25, error_=True)
PriceEngineTest13 = make_fake_engine("test_13", 8000)
PriceEngineTest14 = make_fake_engine("test_14", 7000)
PriceEngineTest15 = make_fake_engine("test_15", 7000)
PriceEngineTest16 = make_fake_engine("test_16", 7000)


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


def test(price_options, engines_names):

    pr_engine = PriceEngines(price_options, engines_names=engines_names)

    we_prices = pr_engine.get_weighted()
    we_median = pr_engine.get_weighted_median(we_prices)
    
    display_table = []
    for we_price in we_prices:
        row = []
        row.append(we_price['name'])
        row.append(we_price['price'])
        row.append(we_price['price_ponderation'])
        row.append(we_price['ponderation'])
        display_table.append(row)

    titles = ['Name', 'Price', 'Ponderation', 'Original Ponderation']

    print("")
    print(tabulate(display_table, headers=titles, tablefmt="pipe"))
    print("")
    print("**Weighted median:** {0}".format(we_median ))
    print("")


if __name__ == '__main__':

    price_options = [
        {"name": "test_1", "ponderation": 0.1605, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_2", "ponderation": 0.2138, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_3", "ponderation": 0.2782, "min_volume":  0.0, "max_delay": 0},
        {"name": "test_4", "ponderation": 0.3475, "min_volume":  0.0, "max_delay": 0}
    ]

    test(price_options, engines_names_1)

    price_options = [
        {"name": "test_5", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_6", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_7", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_8", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0}
    ]

    test(price_options, engines_names_2)
    
    price_options = [
        {"name": "test_9", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_10", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_11", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_12", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0}
    ]

    test(price_options, engines_names_3)

    price_options = [
        {"name": "test_13", "ponderation": 0.2782, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_14", "ponderation": 0.2138, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_15", "ponderation": 0.3475, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_16", "ponderation": 0.1605, "min_volume": 0.0, "max_delay": 0}
    ]

    test(price_options, engines_names_4)

    price_options = [
        {"name": "test_13", "ponderation": 1.0, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_14", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_15", "ponderation": 0.25, "min_volume": 0.0, "max_delay": 0},
        {"name": "test_16", "ponderation": 0.0, "min_volume": 0.0, "max_delay": 0}
    ]

    test(price_options, engines_names_4)
