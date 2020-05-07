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


## Oracle

First we need that the owner of the Oracle create a price feeder, this
is created by governor of the Oracle (MoC Medianizer) contract.

We need some information first. The address of the account that are
going to pay for gas.

Example: `0xfDB628524AD95c95a2C1f8dA9b8Bd92b6478CF6F` you need to
control that account and have funds only to pay transaction gas.

The new price feeder is owned by the user and also have the contract
address. 

Edit **config.json** with this information: MoCMedianizer is oracle address.
PriceFeed is the address of the new contract price feeder. For RIF pricefeeder
take as base and edit: **config_rdoc.json**

Example Mainnet MoC Price Feeder:

```
"addresses": {
        "PriceFeed": "0xfE05Ee3d651670F807Db7dD56e1E0FCBa29B234a",
        "MoCMedianizer": "0x7B19bb8e6c5188eC483b784d6fB5d807a77b21bF"
      }
```

Example Mainnet RIF Price Feeder *( RIF Only):

```
"addresses": {
        "PriceFeed": "0x461750b4824b14c3d9b7702bC6fBB82469082b23",
        "MoCMedianizer": "0x504EfCadFB020d6bBaeC8a5c5BB21453719d0E00",
        "RIF_source_price_btc": "0x7B19bb8e6c5188eC483b784d6fB5d807a77b21bF"
      }
```

**Note:** Only in RIF price feeder we need to set  **RIF_source_price_btc** this is the address of MOC Medianizer,
cause all the price providers are in BTC/RIF, and we do transformation to USD/RIF getting the USD price of BTC from
MOC Main .

**MOC Mainnet network:**


|  Contract  |  Address |
|:---|:---|
|  PriceFeeders  | [List feeds](https://blockscout.com/rsk/mainnet/address/0xf0abcc4cb0b46d9858704eb0c72d9735986b09cf/logs) |
|  Medianizer  | [0x7b19bb8e6c5188ec483b784d6fb5d807a77b21bf](https://blockscout.com/rsk/mainnet/address/0x7b19bb8e6c5188ec483b784d6fb5d807a77b21bf/contracts) |


**RDOC Mainnet network:**


|  Contract  |  Address |  
|:---|:---|
|  FeedFactory  | [0x54878866F5324b56aEE9b6619A1E1a213b2fCC30](https://blockscout.com/rsk/mainnet/address/0x54878866F5324b56aEE9b6619A1E1a213b2fCC30/contracts) |
|  Medianizer  | [0x504EfCadfB020d6Bbaec8a5C5bb21453719d0e00](https://blockscout.com/rsk/mainnet/address/0x504EfCadfB020d6Bbaec8a5C5bb21453719d0e00/contracts) |


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
pricefeed. Edit config.json, there are many networks already preconfigurated, edit the network you want to run
and run the above command passing the network you are going to use:


`python price_feeder.py --network=mocTestnet`

**--config:** Path to config.json 

**--network=local:** Network name in the json


**Usage Docker**

Build

```
docker build -t price_feeder -f Dockerfile .
```

Run

```
docker run -d \
--name price_feeder_1 \
--env ACCOUNT_PK_SECRET=0x9e790b185e5b7f11f2924c7b809936866c38ed3ab3f33e0fbd3cfe791c2cdbd6 \
--env PRICE_FEEDER_NETWORK=local \
price_feeder
```


## Price Ponderation and tickers

[Price ponderation and tickers](https://github.com/money-on-chain/price-feeder/blob/master/docs/PRICE_PONDERATION.md)

## Security and Audits

[Deployed Contracts](https://github.com/money-on-chain/main-RBTC-contract/blob/master/docs/Contracts%20verification.md)
[Audits](https://github.com/money-on-chain/Audits)


## Tutorial

### 1. Pricefeeder RDOC Testnet

WARNING: This guide is only for RIF DoC 

I'm going to use docker method.

1. We need to have our account to sign transactions, also we need pk and funds. In my example I am going to use:
0xbc6d77a5adfa6fb09c3d2cb8b4765d5729e7b8ba

2. Initiate the process of whitelisting sending the address of the account from the step 1 to MOC team.

3. Clone the repository:

```
git clone https://github.com/money-on-chain/price-feeder
cd price-feeder
git checkout master 
```

4. Set the base template config por our deployment

```
cp enviroments/rdoc-testnet-rsk/config.json config.json
```

5. Edit config.json and change to ensure this:

```
"app_mode": "RIF",
...
"uri": "https://public-node.testnet.rsk.co",
"network_id": 31,
...
"addresses": {
        "PriceFeed": "0xE0A3dce741b7EaD940204820B78E7990a136EAC1",
        "MoCMedianizer": "0x9d4b2c05818A0086e641437fcb64ab6098c7BbEc",
        "RIF_source_price_btc": "0x78c892Dc5b7139d0Ec1eF513C9E28eDfAA44f2d4"
      }


```

6. Build docker

```
docker build -t price_feeder -f Dockerfile .
```

7. Run

Replace **(PRIVATE KEY)** with private key

```
docker run -d \
--name price_feeder_1 \
--env ACCOUNT_PK_SECRET=(PRIVATE KEY) \
--env PRICE_FEEDER_NETWORK=local \
price_feeder
```
