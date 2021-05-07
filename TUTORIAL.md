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


### Custom configurations

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


