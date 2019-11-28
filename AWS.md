# AWS Price Feeder

## About

Script for creating the docker image for AWS Fargate usage. Based on the Price Feeder created by Martin Mulone with the only difference that the logs are redirected to sterr/stdout to allow log collection by AWS Cloudwatch and also **the private key is taken from environment variables**

## Usage

### **Building image** 
```
build.sh -e <environment>
```

 Where environment could be

* test: test.moneyonchain.com
* moc-testnet: moc-testnet.moneyonchain.com
* rrc20-mainnet: xxx.moneyonchain.com

_(Feel free to add new implementations here)_


This command will take the ABIs from the version folder corresponding to the implementation.

Finally it will build the docker image.

### **Running image**

In case you want to validate if the image is working as expected you can run the following command

```
docker run  -v ${PWD}/logs:/home/www-data/app/price_feeder/logs <image of your choosing>
```

## Pushing images to AWS Elastic Container Repository (ECR)

Ensure you have installed the latest version of the AWS CLI and Docker.

Make sure you have built your image before pushing it. Then execute **tag_and_push.sh -e  &lt;environment>**

This script will tag with _latest_ and push to the proper repository.

```
Leonels-MacBook-Pro:aws_price_feeder leonelcorso$ bash tag_and_push.sh -e test
The push refers to repository [xx.dkr.ecr.us-west-1.amazonaws.com/moc_price_feeder_test]
a15cffa60880: Pushed 
f31de19de7a0: Pushed 
4b6b8c802c77: Pushed 
8f507683918f: Pushed 
149b595aed7e: Pushed 
0d5470f1b20c: Pushed 
8891d83799da: Pushing [==============>                                    ]  17.87MB/61.37MB
b893e14cc173: Pushed 
2411b83bc413: Pushed 
b82fe1fcc424: Pushing [====>                                              ]  4.121MB/44.52MB
574ea6c52bdd: Pushing [============================>                      ]  3.557MB/6.241MB
d1573fad78d1: Pushing [==================================================>]  4.608kB
14c1ff636882: Pushing [>                                                  ]  526.3kB/91.29MB
48ebd1638acd: Waiting 
31f78d833a92: Waiting 
2ea751c0f96c: Waiting 
7a435d49206f: Waiting 
9674e3075904: Waiting 
831b66a484dc: Waiting 
```

Image should be now available in the AWS repository for Fargate usage

## Setting up the Price Feeder in AWS ECS

Price Feeder are setup as services in AWS ECS. You can follow the screenshots below to understand how to set it up.


There are mandatory environmental variables that you need to take into consideration when creating the task definition

1. PRICE_FEEDER_CONFIG: The configuration of the price feeder as a flattened json (config.json)
2. ACCOUNT_PK_SECRET: The Private Key of the account that the price
   feeder uses. You need to set this as **"valueFrom"** and store the PK
   in AWS System Manager as an **encrypted parameter**
3. ACCOUNT_ADDRESS: The address of the account 
4. PRICE_FEEDER_NAME: The name of the environment where you are deploying
  (test, moc-testnet, rrc20-testnet)
5. AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: these are needed for the
  heartbeat function of the price feeder, as it needs an account that
  has write access to a metric in Cloudwatch

![Diagram](./img/env_variables.png)