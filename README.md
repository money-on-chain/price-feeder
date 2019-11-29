This is the job app that feed contract (price feeder) with price BTC-USD
or RIF-USD

# Money on Chain - Price Feeder

Reference price (BTCUSD) for MoC system is provided via an oracle (the
medianizer), which collates price data from a number of external price
feeds. Take a look to
[Oracle project](https://github.com/money-on-chain/Amphiraos-Oracle)

## Background

**Price Feeds**

Independent price feed operators constantly monitor the reference price
across a number of external sources and will submit updates to the
blockchain.

Price updates are written to the blockchain via price feed contracts which are deployed and owned by feed operators. Price feed contracts which have been whitelisted by the medianizer are able to forward their prices for inclusion in the medianized price.

**The Medianizer**

The medianizer is the smart contract which provides MoC trusted reference price.

It maintains a whitelist of price feed contracts which are allowed to post price updates and a record of recent prices supplied by each address. Every time a new price update is received the median of all feed prices is re-computed and the medianized value is updated.

**Permissions**

The adding and removal of whitelisted price feed addresses is controlled via governance, as is the setting of the `min` parameter - the minimum number of valid feeds required in order for the medianized value to be considered valid.

## Job

This is an job app that run on background, getting the price from
different sources ponderate the final price and saving to **price feeder
contract**.


## Oracle

First we need that the owner of the Oracle create a price feeder, this
is created by governor of the Oracle (MoC Medianizer) contract.

We need some information first. The address of the account that are
going to pay for gas.

Example: `0xfDB628524AD95c95a2C1f8dA9b8Bd92b6478CF6F` you need to
control that account and have funds only to pay transaction gas.

The new price feeder is owned by the user and also have the contract
address. 

Edit config.json with this information: MoCMedianizer is oracle address.
PriceFeed is the address of the new contract price feeder

```
"addresses": {
        "PriceFeed": "0x3442F63Ed9FeF9b9c224Ef58519c588804918bA2",
        "MoCMedianizer": "0x111301D0B6Ea6d588ba50b0eB8be7c02B6271AEA"
      }
```

**Mainnet network:**


|  Contract  |  Address |
|:---|:---|
|  PriceFeeders  | [List feeds](https://blockscout.com/rsk/mainnet/address/0xf0abcc4cb0b46d9858704eb0c72d9735986b09cf/logs) |
|  Medianizer  | [0x7b19bb8e6c5188ec483b784d6fb5d807a77b21bf](https://blockscout.com/rsk/mainnet/address/0x7b19bb8e6c5188ec483b784d6fb5d807a77b21bf/contracts) |


## Price Feeder

**Requirement and installation**
 
*  We need Python 3.6+

Install libraries

`pip install -r requirements.txt`

**Usage Test**

To test price ponderation:

`python price_test.py`

**Usage Job**

Make sure to change **config.json** to point to your network and
pricefeed.

`python price_feeder.py`

Alternatives:

`python price_feeder.py --config=path_to_config.json --network=local`

**--config:** Path to config.json 

**--network=local:** Network name in the json


**Usage Docker**

Build

```
docker build -t price_feeder -f Dockerfile.standalone .
```

Run

```
docker run --rm --name price_feeder_1 price_feeder
```


## Price Ponderation and tickers

[Price ponderation and tickers](https://github.com/money-on-chain/price-feeder/blob/master/PRICE_PONDERATION.md)

### Security and Audits

[Deployed Contracts](https://github.com/money-on-chain/main-RBTC-contract/blob/master/Contracts%20verification.md)
[Audits](https://github.com/money-on-chain/Audits)