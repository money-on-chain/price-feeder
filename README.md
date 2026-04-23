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

1. Copy the example env file and fill in your values:

```
cp .env.example .env
```

2. Edit `.env` — at minimum set `ACCOUNT_PK_SECRET`. See `.env.example` for all available options.

3. Load the env file and run:

```
set -a && source .env && set +a
python app_run_price_feeder.py --config ./enviroments/moc-testnet/config.json
```

**Note:** Never pass the private key directly on the command line — it will be stored in your shell history.

**--config:** Path to config.json or json content (string)


### Docker (Recommended)

Build, change path to correct environment:

```
docker build -t price_feeder -f Dockerfile --build-arg CONFIG=./enviroments/rdoc-testnet/config.json .
```

1. Copy the example env file and fill in your values:

```
cp .env.example .env
```

2. Run using the env file:

```
docker run -d \
--name price_feeder_1 \
--env-file .env \
price_feeder
```

**Note:** Do not pass the private key inline with `--env ACCOUNT_PK_SECRET=...` — it will appear in `docker inspect` output and process listings.

**Production (AWS ECS):** Use ECS `secrets` referencing AWS Secrets Manager or SSM Parameter Store instead of `environment`. This prevents the key from being stored in plaintext in the task definition.

## Security and Audits

[Deployed Contracts](https://github.com/money-on-chain/main-RBTC-contract/blob/master/docs/Contracts%20verification.md)

[Audits](https://github.com/money-on-chain/Audits)


