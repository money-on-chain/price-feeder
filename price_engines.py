import requests
import datetime


def price_engine_bitstamp_btc_usd(session, log, timeout=10):

    engine = 'bitstamp_btc_usd'

    try:
        response = session.get('https://www.bitstamp.net/api/v2/ticker/btcusd/', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['timestamp']))
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_coinbase_btc_usd(session, log, timeout=10):

    engine = 'coinbase_btc_usd'

    try:
        response = session.get('https://api.coinbase.com/v2/prices/BTC-USD/buy', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['amount'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_bitgo_btc_usd(session, log, timeout=10):

    engine = 'bitgo_btc_usd'

    try:
        response = session.get('https://www.bitgo.com/api/v1/market/latest', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['latest']['currencies']['USD']['last'])
        d_price_info['volume'] = float(response_json['latest']['currencies']['USD']['total_vol'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['latest']['currencies']['USD']['timestamp']))
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_bitfinex_btc_usd(session, log, timeout=10):

    engine = 'bitfinex_btc_usd'

    try:
        response = session.get('https://api-pub.bitfinex.com/v2/ticker/tBTCUSD', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_blockchain_btc_usd(session, log, timeout=10):

    engine = 'blockchain_btc_usd'

    try:
        response = session.get('https://blockchain.info/ticker', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['USD']['last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_binance_btc_usd(session, log, timeout=10):

    engine = 'binance_btc_usd'

    try:
        response = session.get('https://api.binance.com/api/v1/ticker/24hr?symbol=BTCUSDT', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['lastPrice'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_kucoin_btc_usd(session, log, timeout=10):

    engine = 'kucoin_btc_usd'

    try:
        response = session.get('https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data']['last'])
        d_price_info['volume'] = float(response_json['data']['vol'])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_kraken_btc_usd(session, log, timeout=10):

    engine = 'kraken_btc_usd'

    try:
        response = session.get('https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['XXBTZUSD']['c'][0])
        d_price_info['volume'] = float(response_json['result']['XXBTZUSD']['v'][1])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_bittrex_btc_usd(session, log, timeout=10):

    engine = 'bittrex_btc_usd'

    try:
        response = session.get('https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC', timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['result']['Last'])
        d_price_info['volume'] = 0.0
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_bitfinex_rif_btc(session, log, timeout=10):

    engine = 'bitfinex_rif_btc'

    try:
        response = session.get('https://api-pub.bitfinex.com/v2/ticker/tRIFBTC',
                               timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json[6])
        d_price_info['volume'] = float(response_json[7])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None


def price_engine_bithumbpro_rif_btc(session, log, timeout=10):

    engine = 'bithumbpro_rif_btc'

    try:
        response = session.get('https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=RIF-BTC',
                               timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        error_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(engine, http_err)
        log.error(error_msg)
        return None, error_msg
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    if not response:
        error_msg = "Error! No response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    if response.status_code != 200:
        error_msg = "Error! Error response from server on get price. Engine: {0}".format(engine)
        log.error(error_msg)
        return None, error_msg

    try:
        response_json = response.json()
        d_price_info = dict()
        d_price_info['price'] = float(response_json['data'][0]['c'])
        d_price_info['volume'] = float(response_json['data'][0]['v'])
        d_price_info['timestamp'] = datetime.datetime.now()
    except Exception as err:
        error_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(engine, err)
        log.error(error_msg)
        return None, error_msg

    return d_price_info, None