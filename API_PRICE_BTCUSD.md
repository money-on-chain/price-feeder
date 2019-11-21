### Price Feeder MOC

Get the price value from:

Main:


1. Bitstamp
2. Bitfinex
3. kraken
4. Coinbase


Alternatives:


5. Binance
6. Bitgo
7. Blockchain 
8. kucoin
9.  Bittrex


Ponderated price is static proportion from a list of feeders. The sum of
all proportions must be equal to 1.

```
Price feeder 1 * proportion 1 = Price proportion 1
Price feeder 2 * proportion 2 = Price proportion 2
...

Final price = Price proportion 1 + Price proportion 2 ...
```

#### Example ponderated price:

```
{
"price_fetchers": ["bitstamp", "bitfinex", "kraken", "coinbase"],
"price_ponderations": [0.25, 0.25, 0.25, 0.25]
}
```


**Case 1:**

In case 1, we have all the prices from price feeders

```
{
   'bitfinex':{
      'ponderated':'2037.95',
      'portion':0.25,
      'price':'8151.80'
   },
   'bitstamp':{
      'ponderated':'2031.27',
      'portion':0.25,
      'price':'8125.07'
   },
   'coinbase':{
      'ponderated':'2043.05',
      'portion':0.25,
      'price':'8172.21'
   },
   'kraken':{
      'ponderated':'2031.85',
      'portion':0.25,
      'price':'8127.40'
   }
}
```
**price:** 8144.119999999999

**Case 2:**

In case 2, one price fetcher fail

```
{
   'bitfinex':{
      'ponderated':'2719.00',
      'portion':0.3333333333333333,
      'price':'8157.00'
   },
   'bitstamp':{
      'ponderated':'2710.02',
      'portion':0.3333333333333333,
      'price':'8130.06'
   },
   'kraken':{
      'ponderated':'2713.20',
      'portion':0.3333333333333333,
      'price':'8139.60'
   }
}
```

**price:** 8142.22


**Case 3:**

In case 3, two price fetcher fail

```
{
   'bitfinex':{
      'ponderated':'4079.55',
      'portion':0.5,
      'price':'8159.10'
   },
   'kraken':{
      'ponderated':'4073.40',
      'portion':0.5,
      'price':'8146.80'
   }
}
```

**Price:** 8152.950000000001




#### Example ponderated price (REAL):

```
{
"price_fetchers": ["bitstamp", "bitfinex", "kraken", "coinbase"],
"price_ponderations": [0.2138, 0.2782, 0.1605, 0.3475],
}
```


**Case 1:**

In case 1, we have all the prices from price feeders

```
{
   'bitfinex':{
      'ponderated':'2268.58',
      'portion':0.2782,
      'price':'8154.50'
   },
   'bitstamp':{
      'ponderated':'1737.35',
      'portion':0.2138,
      'price':'8126.03'
   },
   'coinbase':{
      'ponderated':'2839.72',
      'portion':0.3475,
      'price':'8171.86'
   },
   'kraken':{
      'ponderated':'1304.64',
      'portion':0.1605,
      'price':'8128.60'
   }
}
```
**price:** 8150.288764


**Case 2:**

In case 2, one price fetcher fail

```
{
   'bitfinex':{
      'ponderated':'3212.28',
      'portion':0.39403333333333335,
      'price':'8152.30'
   },
   'bitstamp':{
      'ponderated':'2677.55',
      'portion':0.32963333333333333,
      'price':'8122.80'
   },
   'kraken':{
      'ponderated':'2244.41',
      'portion':0.2763333333333333,
      'price':'8122.10'
   }
}
```

**price:** 8134.23055


Then set the price average in the contract.

This is the a slice of python script:

```
    def get_price_from_sources(self):

        # create persistent HTTP connection
        session = requests.Session()
        l_prices = list()
        d_info = dict()

        price_fetchers = price_poster.options['price_fetchers']
        min_volume = price_poster.options['min_volume']

        # coinbase
        if 'coinbase' in price_fetchers:
            price_info, price_err = self.price_engine_coinbase_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['coinbase'] = d_pricer

        # bitstamp
        if 'bitstamp' in price_fetchers:
            price_info, price_err = self.price_engine_bitstamp_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitstamp'] = d_pricer

        # bitgo
        if 'bitgo' in price_fetchers:
            price_info, price_err = self.price_engine_bitgo_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitgo'] = d_pricer

        # bitfinex
        if 'bitfinex' in price_fetchers:
            price_info, price_err = self.price_engine_bitfinex_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bitfinex'] = d_pricer

        # blockchain
        if 'blockchain' in price_fetchers:
            price_info, price_err = self.price_engine_blockchain_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['blockchain'] = d_pricer

        # bittrex
        if 'bittrex' in price_fetchers:
            price_info, price_err = self.price_engine_bittrex_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['bittrex'] = d_pricer

        # kraken
        if 'kraken' in price_fetchers:
            price_info, price_err = self.price_engine_kraken_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['kraken'] = d_pricer

        # kucoin
        if 'kucoin' in price_fetchers:
            price_info, price_err = self.price_engine_kucoin_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['kucoin'] = d_pricer

        # binance
        if 'binance' in price_fetchers:
            price_info, price_err = self.price_engine_binance_btc_usd(session)
            if price_info:
                if price_info['volume'] >= min_volume:
                    l_prices.append(price_info['price'])
                    d_pricer = dict()
                    d_pricer['price'] = price_info['price']
                    d_pricer['volume'] = price_info['volume']
                    d_info['binance'] = d_pricer

        return l_prices, d_info

    def get_ponderated_from_sources(self):
        """ Ponderated """

        price_ponderations = price_poster.options['price_ponderations']
        price_fetchers = price_poster.options['price_fetchers']

        if len(price_ponderations) != len(price_fetchers):
            raise Exception("Error! Price ponderations and price feeder list not equal!")

        prices_list, prices_dict = self.get_price_from_sources()

        l_ponderated = list()
        d_ponderated = dict()
        missing_portions = 0.0

        if len(prices_list) != len(price_ponderations):
            for index, price_name in enumerate(price_fetchers):
                if price_name not in prices_dict:
                    missing_portions += price_ponderations[index]
                    continue

        eq_missing_portions = missing_portions / len(prices_list)

        for index, price_name in enumerate(price_fetchers):
            if price_name not in prices_dict:
                continue

            portion = price_ponderations[index] + eq_missing_portions
            p_ponderated = prices_dict[price_name]['price'] * portion
            l_ponderated.append(p_ponderated)

            d_info = dict()
            d_info['price'] = format(prices_dict[price_name]['price'], '.2f')
            d_info['portion'] = portion
            d_info['ponderated'] = format(p_ponderated, '.2f')
            d_ponderated[price_name] = d_info

        log.info(pp.pprint(d_ponderated))

        return sum(l_ponderated)

        
    def price_setter(self, last_price):

        price_medianizer = self.get_medianizer_from_sources()

        price_to_set = price_medianizer * 10 ** 18
        if last_price != price_medianizer:
            price_poster.post_price(price_to_set)
        else:
            log.info("WARNING! NOT SETTING is the same to last!")

        return price_medianizer

    def price_setter_loop(self):

        killer = GracefulKiller()
        last_price = 0.0
        while not killer.kill_now:

            start_time = time.time()
            last_price = self.price_setter(last_price)
            duration = time.time() - start_time

            if duration > self.options['timeout']:
                log_timeout.info("TIMEOUT! Slow Setting price! Duration: {0}".format(duration))

            time.sleep(self.options['wait'])
```



### APIs

Coinbase

Curl:

```
curl https://api.coinbase.com/v2/prices/BTC-USD/buy
```

Response

```
{"data":{"base":"BTC","currency":"USD","amount":"8305.14"}}
```

#### Bitstamp

Curl:

```
curl https://www.bitstamp.net/api/v2/ticker/btcusd/
```

Response:

```
{
   "high":"8222.73",
   "last":"8193.54",
   "timestamp":"1570461046",
   "bid":"8187.95",
   "vwap":"7978.90",
   "volume":"9855.75437960",
   "low":"7763.54",
   "ask":"8195.00",
   "open":"7863.75"
}
```

#### Bitgo


Curl:

```
curl https://www.bitgo.com/api/v1/market/latest
```

Response:

```
{
   "latest":{
      "blockchain":{
         "cacheTime":1570461031203,
         "transactions":303336,
         "totalbc":17978837.5
      },
      "currencies":{
         "cacheTime":1570461117022,
         "JPY":{
            "24h_avg":850130.92,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":877628.64,
            "bid":876467.61,
            "ask":876896.85
         },
         "DKK":{
            "24h_avg":54004.99,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":55751.8,
            "bid":55678.04,
            "ask":55705.31
         },
         "TRY":{
            "24h_avg":45737.02,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":47216.4,
            "bid":47153.94,
            "ask":47177.03
         },
         "CLP":{
            "24h_avg":5697136.72,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":5881412.19,
            "bid":5873631.56,
            "ask":5876508.11
         },
         "UYU":{
            "24h_avg":295339.72,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":304892.56,
            "bid":304489.22,
            "ask":304638.34
         },
         "ZAR":{
            "24h_avg":120371.98,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":124265.44,
            "bid":124101.05,
            "ask":124161.83
         },
         "CNY":{
            "24h_avg":56823.51,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":58661.49,
            "bid":58583.88,
            "ask":58612.57
         },
         "GBP":{
            "24h_avg":6449.87,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":6658.49,
            "bid":6649.69,
            "ask":6652.94
         },
         "ARS":{
            "24h_avg":460341.68,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":475231.56,
            "bid":474602.87,
            "ask":474835.3
         },
         "USD":{
            "24h_avg":7949.12,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":8206.24,
            "bid":8195.38,
            "ask":8199.4
         },
         "EUR":{
            "24h_avg":7230.16,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":7464.02,
            "bid":7454.14,
            "ask":7457.79
         },
         "NOK":{
            "24h_avg":72547.04,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":74893.59,
            "bid":74794.51,
            "ask":74831.14
         },
         "AUD":{
            "24h_avg":11782.59,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":12163.7,
            "bid":12147.61,
            "ask":12153.56
         },
         "COP":{
            "24h_avg":27357067.09,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":28241939.02,
            "bid":28204577.22,
            "ask":28218390.13
         },
         "SEK":{
            "24h_avg":78695.54,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":81240.97,
            "bid":81133.5,
            "ask":81173.23
         },
         "CAD":{
            "24h_avg":10572.72,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":10914.69,
            "bid":10900.25,
            "ask":10905.59
         },
         "INR":{
            "24h_avg":564232.75,
            "total_vol":53794.13,
            "timestamp":1570461114,
            "last":582483.02,
            "bid":581712.44,
            "ask":581997.33
         }
      },
      "coin":"btc"
   }
}
```


#### Bitfinex

Curl:

```
curl https://api-pub.bitfinex.com/v2/ticker/tBTCUSD
```

Response:

```
[
  BID, 
  BID_SIZE, 
  ASK, 
  ASK_SIZE, 
  DAILY_CHANGE, 
  DAILY_CHANGE_PERC, 
  LAST_PRICE, 
  VOLUME, 
  HIGH, 
  LOW
]
```

```
[8194.6,26.470741979999996,8194.7,23.017177009999997,114.6,0.0142,8194.6,7829.6666724,8250,7793.2]
```


#### Kraken

Curl:

```
curl https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD
```

Response:

```
{
   "error":[

   ],
   "result":{
      "XXBTZUSD":{
         "a":[
            "8202.20000",
            "2",
            "2.000"
         ],
         "b":[
            "8201.50000",
            "1",
            "1.000"
         ],
         "c":[
            "8202.20000",
            "0.02045260"
         ],
         "v":[
            "2324.04855930",
            "5245.98195665"
         ],
         "p":[
            "8239.37411",
            "8232.62321"
         ],
         "t":[
            6253,
            14356
         ],
         "l":[
            "8150.00000",
            "8127.50000"
         ],
         "h":[
            "8348.00000",
            "8348.00000"
         ],
         "o":"8213.40000"
      }
   }
}
```

References:


```
<pair_name> = nombre del par
    a = oferta array(<precio>, <lote completo de volumen>, <lote del volumen>),
    b = demanda array(<precio>, <lote completo de volumen>, <lote del volumen>),
    c = último trade cerrado array(<precio>, <lote del volumen>),
    v = volumen array(<hoy>, <últimas 24 horas>),
    p = precio del volumen medio array(<hoy>, <últimas 24 horas>),
    t = número de operaciones array(<hoy>, <últimas 24 horas>),
    l = mínimo array(<hoy>, <últimas 24 horas>),
    h = máximo array(<hoy>, <últimas 24 horas>),
    o = precio de apertura hoy
```


Documentation:

```
https://www.kraken.com/features/api#public-market-data
```


#### Blockchain

Curl:

```
curl https://blockchain.info/ticker
```

Response:

```
{
  "USD" : {"15m" : 8215.71, "last" : 8215.71, "buy" : 8215.71, "sell" : 8215.71, "symbol" : "$"},
  "AUD" : {"15m" : 12177.7, "last" : 12177.7, "buy" : 12177.7, "sell" : 12177.7, "symbol" : "$"},
  "BRL" : {"15m" : 33391.08, "last" : 33391.08, "buy" : 33391.08, "sell" : 33391.08, "symbol" : "R$"},
  "CAD" : {"15m" : 10923.89, "last" : 10923.89, "buy" : 10923.89, "sell" : 10923.89, "symbol" : "$"},
  "CHF" : {"15m" : 8167.51, "last" : 8167.51, "buy" : 8167.51, "sell" : 8167.51, "symbol" : "CHF"},
  "CLP" : {"15m" : 5889838.99, "last" : 5889838.99, "buy" : 5889838.99, "sell" : 5889838.99, "symbol" : "$"},
  "CNY" : {"15m" : 58729.15, "last" : 58729.15, "buy" : 58729.15, "sell" : 58729.15, "symbol" : "¥"},
  "DKK" : {"15m" : 55821.9, "last" : 55821.9, "buy" : 55821.9, "sell" : 55821.9, "symbol" : "kr"},
  "EUR" : {"15m" : 7485.13, "last" : 7485.13, "buy" : 7485.13, "sell" : 7485.13, "symbol" : "€"},
  "GBP" : {"15m" : 6664.09, "last" : 6664.09, "buy" : 6664.09, "sell" : 6664.09, "symbol" : "£"},
  "HKD" : {"15m" : 64449.95, "last" : 64449.95, "buy" : 64449.95, "sell" : 64449.95, "symbol" : "$"},
  "INR" : {"15m" : 583232.66, "last" : 583232.66, "buy" : 583232.66, "sell" : 583232.66, "symbol" : "₹"},
  "ISK" : {"15m" : 1018666.14, "last" : 1018666.14, "buy" : 1018666.14, "sell" : 1018666.14, "symbol" : "kr"},
  "JPY" : {"15m" : 878608.5, "last" : 878608.5, "buy" : 878608.5, "sell" : 878608.5, "symbol" : "¥"},
  "KRW" : {"15m" : 9829456.21, "last" : 9829456.21, "buy" : 9829456.21, "sell" : 9829456.21, "symbol" : "₩"},
  "NZD" : {"15m" : 13049.51, "last" : 13049.51, "buy" : 13049.51, "sell" : 13049.51, "symbol" : "$"},
  "PLN" : {"15m" : 32377.21, "last" : 32377.21, "buy" : 32377.21, "sell" : 32377.21, "symbol" : "zł"},
  "RUB" : {"15m" : 532776.15, "last" : 532776.15, "buy" : 532776.15, "sell" : 532776.15, "symbol" : "RUB"},
  "SEK" : {"15m" : 81333.56, "last" : 81333.56, "buy" : 81333.56, "sell" : 81333.56, "symbol" : "kr"},
  "SGD" : {"15m" : 11342.18, "last" : 11342.18, "buy" : 11342.18, "sell" : 11342.18, "symbol" : "$"},
  "THB" : {"15m" : 250168.22, "last" : 250168.22, "buy" : 250168.22, "sell" : 250168.22, "symbol" : "฿"},
  "TWD" : {"15m" : 253822.63, "last" : 253822.63, "buy" : 253822.63, "sell" : 253822.63, "symbol" : "NT$"}
```


#### p2pb2b

Curl:

```
curl https://api.p2pb2b.io/api/v1/public/ticker?market=BTC_USD
```

Response:

```
{
   "success":true,
   "message":"",
   "result":{
      "bid":"8127.77",
      "ask":"8275.74",
      "open":"8223.84",
      "high":"8300",
      "low":"8102.97",
      "last":"8210.45",
      "volume":"28110.037934",
      "deal":"230589190.71907289",
      "change":"0.64"
   },
   "cache_time":1570541411.681132,
   "current_time":1570541411.681221
}
```


#### Bittrex


Reference:

```
https://bittrex.github.io/api/v1-1
```

Curl:


```
curl https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC
```

Response:

```
{
   "success":true,
   "message":"",
   "result":{
      "Bid":8218.12100000,
      "Ask":8218.12200000,
      "Last":8219.89900000
   }
}
```


#### Binance

Documentation

```
https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
```

Curl

```
curl https://api.binance.com/api/v1/ticker/24hr?symbol=BTCUSDT
```

Response

```
{
   "symbol":"BTCUSDT",
   "priceChange":"49.42000000",
   "priceChangePercent":"0.606",
   "weightedAvgPrice":"8210.52120244",
   "prevClosePrice":"8150.00000000",
   "lastPrice":"8199.59000000",
   "lastQty":"0.07518100",
   "bidPrice":"8196.76000000",
   "bidQty":"0.03292800",
   "askPrice":"8199.56000000",
   "askQty":"0.44597200",
   "openPrice":"8150.17000000",
   "highPrice":"8325.00000000",
   "lowPrice":"8112.03000000",
   "volume":"43952.84578500",
   "quoteVolume":"360875772.22513840",
   "openTime":1570456846606,
   "closeTime":1570543246606,
   "firstId":187108982,
   "lastId":187557702,
   "count":448721
}
```

Symbols list:

```
curl https://api.binance.com/api/v1/exchangeInfo
```


#### Kucoin

Documentation

```
https://docs.kucoin.com/#faq
```

Curl


```
curl https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT
```

Response

```
{
   "code":"200000",
   "data":{
      "symbol":"BTC-USDT",
      "high":"8324",
      "vol":"739.43856863",
      "last":"8168.5",
      "low":"8108.1",
      "buy":"8166.7",
      "sell":"8166.8",
      "changePrice":"35.4",
      "time":1570544104124,
      "averagePrice":"7950.14790622",
      "changeRate":"0.0043",
      "volValue":"6067456.910194385"
   }
}
```


References:

```
https://coinmarketcap.com/rankings/exchanges/
https://www.coingecko.com/en/exchanges/mxc#trust_score
```


List exchanges by trust

```
https://www.coingecko.com/en/exchanges
```