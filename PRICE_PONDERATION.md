# Price ponderation

### Price BTC-USD ticker

| Nº        | Name        | Ponderation    | Api URI  |
| :--------:  | :----------- | ------------   | ----------------- |
| 1 |  coinbase | 0.3475 | https://api.coinbase.com/v2/prices/spot?currency=USD |
| 2 |  bitfinex | 0.2782 | https://api-pub.bitfinex.com/v2/ticker/tBTCUSD |
| 3 |  bitstamp | 0.2138 | https://www.bitstamp.net/api/v2/ticker/btcusd/ |
| 4 |  kraken | 0.1605 | https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD |


#### Example 1


| Name        | Price        | Ponderation    |   Original Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |-------------------- |
| test_1 |  7250.1 | 0.1605 | 0.1605 |  |
| test_2 |  7258.32 | 0.2138 | 0.2138 |  |
| test_3 |  7283.81 | 0.2782 | 0.2782 | <---- |
| test_4 |  7286.25 | 0.3475 | 0.3475 |  |


**Weighted median:** 7283.81

#### Example 2

| Name        | Price        | Ponderation    |   Original Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |-------------------- |
| test_5 |  7250.1 | 0.1605 | 0.1605 |  |
| test_6 |  7283.81 | 0.2782 | 0.2782 |  |
| test_7 |  7286.25 | 0.3475 | 0.3475 | <----- |
| test_8 |  7984.15 | 0.2138 | 0.2138 |  |


**Weighted median:** 7286.25


#### Example 3

| Name        | Price        | Ponderation    |   Original Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |-------------------- |
| test_9 |  7250.1 | 0.2318 | 0.1605 |  |
| test_10 |  7283.81 | 0.3495 | 0.2782 | <----- |
| test_11 |  7286.25 | 0.4188 | 0.3475 |  |

**Weighted median:** 7283.81

#### Example 4


| Name        | Price        | Ponderation    |   Original Ponderation    |             |
| :--------:  | :----------- | ------------   | -------------------- |-------------------- |
| test_13 |  8000 | 0.2782 | 0.2782 |  |
| test_14 |  7000 | 0.2138 | 0.2138 | <----- |
| test_15 |  7000 | 0.3475 | 0.3475 |  |
| test_16 |  7000 | 0.1605 | 0.1605 |  |

**Weighted median:** 7000


#### Example 5


| Name        | Price        | Ponderation    | Original Ponderation |  |
| :--------:  | :----------- | ------------   | ----------------- |--------------------- |
| test_13 |  8000 | 0.5 | 0.2782 |  |
| test_14 |  7000 | 0.5 | 0.2138 |  |
| test_15 |  fail | - | 0.3475 |  |
| test_16 |  fail | - | 0.1605 |  |


**Weighted median:** N/A Price not set, need at least 3 prices.
