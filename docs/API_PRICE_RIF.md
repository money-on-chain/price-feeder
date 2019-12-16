### API RIF 

Exchanges:

``` 
https://www.rifos.org/rif-token/
```






```
```

#### Bithump pro API


Documentation

```
https://github.com/bithumb-pro/bithumb.pro-official-api-docs/blob/master/rest-api.md
```

All symbols

```
curl https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=ALL
```

**RIF-USDT**

Curl:

```
curl https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=RIF-USDT
```

Response:

```
{
   "data":[
      {
         "p":"-0.0056",
         "ver":"159289",
         "vol":"841544.467975",
         "c":"0.1067",
         "s":"RIF-USDT",
         "v":"7868150.52",
         "h":"0.1075",
         "l":"0.1065"
      }
   ],
   "code":"0",
   "msg":"success",
   "timestamp":1570627145470
}
```

**RIF-BTC**

Curl

```
curl https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=RIF-BTC
```

Response:

```
{
   "data":[
      {
         "p":"0.0000",
         "ver":"142866",
         "vol":"36.1162333754",
         "c":"0.00001307",
         "s":"RIF-BTC",
         "v":"2760147.94",
         "h":"0.00001310",
         "l":"0.00001307"
      }
   ],
   "code":"0",
   "msg":"success",
   "timestamp":1570627045996
}
```




#### Bitfinex

Curl:

```
curl https://api-pub.bitfinex.com/v2/ticker/tRIFBTC
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
[
0.00001251,
509752.75980585004,
0.0000134,
215294.88103356995,
-3.3e-7,
-0.0033,
0.00001284,
450845.11631119,
0.0000142,
0.00001251]
```


```
curl https://api-pub.bitfinex.com/v2/ticker/tRIFUSD
```

```
[
0.078032,
1060861.14404857,
0.1154,
39448.13816078,
0,
0,
0.11,
32,
0.11,
0.11]
```


#### Coincodex


Get all coins

```
curl https://coincodex.com/apps/coincodex/cache/all_coins.json -o all_coins.json
```

Get coin

```
curl https://coincodex.com/api/coincodex/get_coin/RIF
```

Get the info

```
{
   "symbol":"RIF",
   "coin_name":"RIF Token",
   "shortname":"rif-token",
   "slug":"rif-token",
   "display_symbol":"RIF",
   "display":"true",
   "release_date":null,
   "ico_price":null,
   "today_open":0.139197112,
   "market_cap_rank":72,
   "volume_rank":145,
   "description":"<p>The RIF project stands for Root Infrastructure Framework Open Standard&nbsp;which provides a one-stop source for blockchain infrastructure services.<\/p>\n",
   "price_high_24_usd":0.140672394,
   "price_low_24_usd":0.136849907,
   "start":null,
   "end":null,
   "is_promoted":null,
   "message":"",
   "website":"https:\/\/www.rifos.org\/",
   "whitepaper":"https:\/\/www.rifos.org\/#",
   "total_supply":null,
   "supply":488688390,
   "platform":"",
   "how_to_buy_url":null,
   "last_price_usd":0.136744009,
   "price_change_1H_percent":"-0.540000000",
   "price_change_1D_percent":"-0.840000000",
   "price_change_7D_percent":"-3.810000000",
   "price_change_30D_percent":"1.240000000",
   "price_change_90D_percent":"89.310000000",
   "price_change_180D_percent":"81.010000000",
   "price_change_365D_percent":"-24.670000000",
   "price_change_YTD_percent":"-24.670000000",
   "volume_24_usd":4229873.1724401,
   "trading_since":"2019-01-17 00:00:00",
   "stages_start":null,
   "stages_end":null,
   "include_supply":"true",
   "ath_usd":"0.221804",
   "ath_date":"2019-01-17 04:20:00",
   "not_trading_since":null,
   "last_update":"2019-09-11 14:08:03",
   "social":{
      "explorer":"https:\/\/explorer.rsk.co\/address\/0x2acc95758f8b5f583470ba265eb685a8f45fc9d5",
      "twitter":"https:\/\/twitter.com\/rif_os",
      "reddit":"https:\/\/www.reddit.com\/r\/rifos",
      "github":"https:\/\/github.com\/riflabs",
      "telegram":"https:\/\/t.me\/rif_os"
   },
   "socials":[
      {
         "name":"explorer",
         "id":"78649",
         "coincodex_coin_symbol":"RIF",
         "coincodex_socials_id":"13",
         "value":"https:\/\/explorer.rsk.co\/address\/0x2acc95758f8b5f583470ba265eb685a8f45fc9d5",
         "label":""
      },
      {
         "name":"twitter",
         "id":"78650",
         "coincodex_coin_symbol":"RIF",
         "coincodex_socials_id":"3",
         "value":"https:\/\/twitter.com\/rif_os",
         "label":""
      },
      {
         "name":"reddit",
         "id":"78651",
         "coincodex_coin_symbol":"RIF",
         "coincodex_socials_id":"2",
         "value":"https:\/\/www.reddit.com\/r\/rifos",
         "label":""
      },
      {
         "name":"github",
         "id":"78652",
         "coincodex_coin_symbol":"RIF",
         "coincodex_socials_id":"9",
         "value":"https:\/\/github.com\/riflabs",
         "label":""
      },
      {
         "name":"telegram",
         "id":"78653",
         "coincodex_coin_symbol":"RIF",
         "coincodex_socials_id":"6",
         "value":"https:\/\/t.me\/rif_os",
         "label":""
      }
   ]
}
```

we need to know: **last_price_usd**


https://coincodex.com/api/exchange/get_markets_by_coin/rif/


https://apidocs.bithumb.com/docs/ticker


curl https://api.bithumb.com/public/ticker/rif


#### Coin market API
 
https://coinmarketcap.com/api/documentation/v1/#


API: 1a913b25-14f6-4f04-8414-30c4ef409959

curl -H "X-CMC_PRO_API_KEY: 1a913b25-14f6-4f04-8414-30c4ef409959" -H "Accept: application/json" -d "start=1&limit=5000&convert=USD" -G https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest

curl -H "X-CMC_PRO_API_KEY: 1a913b25-14f6-4f04-8414-30c4ef409959" -H "Accept: application/json" -d "start=1&limit=5000&convert=USD" -G https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest


```
curl -H "X-CMC_PRO_API_KEY: 1a913b25-14f6-4f04-8414-30c4ef409959" -H "Accept: application/json" -d "start=1&limit=1&convert=RIF" -G https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest
```


#### Others


```
curl https://api.bithumb.com/public/ticker/BTC
curl https://api.bithumb.com/public/ticker/USDTRIF
```

