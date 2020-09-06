import requests
import datetime


class Base(object):

    name        = "base_engine"
    description = "Base Engine"
    uri         = "http://api.pricefetcher.com/BTCUSD"
    convert     = "BTC_USD"

    def __init__(self, log, timeout=10, uri=None):
        self.log = log
        self.timeout = timeout
        if uri:
            self.uri = uri

    def send_alarm(self, message, level=0):
        self.log.error(message)

    def fetch(self, session):

        try:
            response = session.get(self.uri, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            err_msg = "Error! Error response from server on get price. Engine: {0}. {1}".format(self.name, http_err)
            self.send_alarm(err_msg)
            return None, err_msg
        except Exception as err:
            err_msg = "Error. Error response from server on get price. Engine: {0}. {1}".format(self.name, err)
            self.send_alarm(err_msg)
            return None, err_msg

        if not response:
            err_msg = "Error! No response from server on get price. Engine: {0}".format(self.name)
            self.send_alarm(err_msg)
            return None, err_msg

        if response.status_code != 200:
            err_msg = "Error! Error response from server on get price. Engine: {0}".format(self.name)
            self.send_alarm(err_msg)
            return None, err_msg

        return response, ""

    @staticmethod
    def map(response_json):

        d_price_info = dict()
        d_price_info['price'] = float(response_json['last'])
        d_price_info['volume'] = float(response_json['volume'])
        d_price_info['timestamp'] = datetime.datetime.utcfromtimestamp(int(response_json['timestamp']))

        return d_price_info

    def get_price(self, session):

        r, err_msg = self.fetch(session)
        if not r:
            return None, err_msg

        try:
            response_json = r.json()
            d_price_info = self.map(response_json)
        except Exception:
            err_msg = "Error. Error response from server on get price. Engine: {0}. ".format(self.name)
            self.send_alarm(err_msg)
            return None, err_msg

        return d_price_info, None
