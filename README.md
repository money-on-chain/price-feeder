This is the job app that feed contract (price feeder) with price BTC-USD | RIF-USD | ETH-BTC | USDT-USD

# Money on Chain - Price Feeder

Reference price (BTCUSD) for MoC system is provided via an oracle (the
medianizer), which collates price data from a number of external price
feeds. Take a look to:

* [Oracle project](https://github.com/money-on-chain/Amphiraos-Oracle)

* [Proxy Oracle](https://github.com/money-on-chain/Proxy_Oracle): If you don't want to change oracle address
when we change to new generation of oracle (decentralized oracle)

## Background

**Price Feeds**

Independent price feed operators constantly monitor the reference price
across a number of external sources and will submit updates to the
blockchain.

Price updates are written to the blockchain via price feed contracts which are deployed and owned by feed operators. 
Price feed contracts which have been whitelisted by the medianizer are able to forward their prices for 
inclusion in the medianized price.

**The Medianizer**

The medianizer is the smart contract which provides MoC trusted reference price.

It maintains a whitelist of price feed contracts which are allowed to post price updates and a record of recent 
prices supplied by each address. Every time a new price update is received the median of all feed prices is 
re-computed and the medianized value is updated.

**Permissions**

The adding and removal of whitelisted price feed addresses is controlled via governance, as is the setting of 
the `min` parameter - the minimum number of valid feeds required in order for the medianized value to 
be considered valid.

## Job

This is an job app that run on background, getting the price from
different sources ponderate the final price and saving to **price feeder
contract**.


## Price sources

Prices from exchanges, take a look to [Prices source](https://github.com/money-on-chain/moc_prices_source)


## Creation of price feeder

First we need that the owner of the Oracle create a price feeder, this
is created by governor of the Oracle (MoC Medianizer) contract.

We need some information first. The address of the account that are
going to pay for gas.

Example: `0xfDB628524AD95c95a2C1f8dA9b8Bd92b6478CF6F` you need to
control that account and have funds only to pay transaction gas.

The new price feeder is owned by the user and also have the contract
address. 


## Usage

### Commandline

**Requirement and installation**
 
*  Required Python 3.10

Install libraries

`pip install -r requirements.txt`

**Usage Job**

There are many networks already preconfigurated see enviroments/ folder.

`export ACCOUNT_PK_SECRET=(Your PK)`

`python app_run_price_feeder.py --config ./enviroments/moc-testnet/config.json`

**Note:** Replace (Your PK) with your private key owner of the account.

**--config:** Path to config.json or json content (string)

#### Custom node instead using of public node

If you want to use your custom private node pass as environment settings, before running price feeder:

`export APP_CONNECTION_URI=https://public-node.rsk.co`

#### Custom config

If you want to use your custom settings, before running price feeder:

`export APP_CONFIG=....`


### Docker (Recommended)

Build, change path to correct environment

```
docker build -t price_feeder -f Dockerfile --build-arg CONFIG=./enviroments/rdoc-testnet/config.json .
```

Run, replace ACCOUNT_PK_SECRET  with your private key owner of the account

```
docker run -d \
--name price_feeder_1 \
--env ACCOUNT_PK_SECRET=asdfasdfasdf \
price_feeder
```

## Security and Audits

[Deployed Contracts](https://github.com/money-on-chain/main-RBTC-contract/blob/master/docs/Contracts%20verification.md)

[Audits](https://github.com/money-on-chain/Audits)


