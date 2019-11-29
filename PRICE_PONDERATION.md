# Price ponderation

### Price BTC-USD ticker

| Nº        | Name        | Ponderation    | Api ticker URI  |
| :--------:  | :----------- | ------------   | ----------------- |
| 1 |  coinbase | 0.2350 | https://api.coinbase.com/v2/prices/spot?currency=USD |
| 2 |  bitfinex | 0.1867 | https://api-pub.bitfinex.com/v2/ticker/tBTCUSD |
| 3 |  bitstamp | 0.1918 | https://www.bitstamp.net/api/v2/ticker/btcusd/ |
| 4 |  kraken | 0.1608 | https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD |
| 5 |  gemini | 0,0880 | https://api.gemini.com/v2/ticker/BTCUSD |
| 6 |  okcoin | 0,0680 | https://www.okcoin.com/api/spot/v3/instruments/BTC-USD/ticker |
| 7 |  itbit | 0,0696 | https://api.itbit.com/v1/markets/XBTUSD/ticker |


#### Example 1


| Name        | Price        | Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |
| bitstamp |  7.542,7600 | 0,1918 |   |
| bitfinex | 7.587,7854 | 0,1867 |  |
| kraken |  7.554,2000 | 0,1608 |  |
| coinbase | 7.546,9150 | 0,2350 | <---- |
| gemini | 7.545,2800 | 0,0880 | |
| okcoin | 7.549,6200 | 0,0680 | |
| itbit | 7.554,7500 | 0,0696 | |


**Weighted median:** 7546,915

#### Example 2

| Name        | Price        | Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |
| bitstamp | 7.535,9900 | 0,1918 | <----  |
| bitfinex | 7.579,1000 | 0,1867 |  |
| kraken |  7.538,1000 | 0,1608 |  |
| coinbase | 7.535,4550 | 0,2350 |  |
| gemini | 7.533,7100 | 0,0880 | |
| okcoin | 7.536,8300 | 0,0680 | |
| itbit | 7.536,7500 | 0,0696 | |


**Weighted median:** 7.535,99


#### Example 3

| Name        | Price        | Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |
| bitstamp | 7.563,0100 | 0,2431 |   |
| bitfinex | - | - |  |
| kraken |  7.553,3000 | 0,2121 |  |
| coinbase | 7.554,9950 | 0,2863 | <---- |
| gemini | 7.550,0000 | 0,1393 | |
| okcoin | 7.546,0100 | 0,1193 | |
| itbit | - | - | |

**Weighted median:** 7554,995


#### Example 4


| Name        | Price        | Ponderation    | Original Ponderation |  |
| :--------:  | :----------- | ------------   | ----------------- |--------------------- |
| test_13 |  8000 | 0.5 | 0.2782 |  |
| test_14 |  7000 | 0.5 | 0.2138 |  |
| test_15 |  fail | - | 0.3475 |  |
| test_16 |  fail | - | 0.1605 |  |


**Weighted median:** N/A Price not set, need at least 3 prices.
