FROM python:3.7

# Autor
LABEL maintainer='martin.mulone@moneyonchain.com'

RUN apt-get update && \
    apt-get install -y \
        locales

RUN echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN brownie networks add RskNetwork rskTestnetPublic host=https://public-node.testnet.rsk.co chainid=31 explorer=https://blockscout.com/rsk/mainnet/api
RUN brownie networks add RskNetwork rskTestnetPrivate host=http://moc-rsk-node-testnet.moneyonchain.com:4454 chainid=31 explorer=https://blockscout.com/rsk/mainnet/api
RUN brownie networks add RskNetwork rskTestnetCustom host=$BROWNIE_CUSTOM_HOST_TESTNET chainid=31 explorer=https://blockscout.com/rsk/mainnet/api
RUN brownie networks add RskNetwork rskMainnetPublic host=https://public-node.rsk.co chainid=30 explorer=https://blockscout.com/rsk/mainnet/api
RUN brownie networks add RskNetwork rskMainnetPrivate host=http://moc-rsk-node-mainnet.moneyonchain.com:4454 chainid=30 explorer=https://blockscout.com/rsk/mainnet/api
RUN brownie networks add RskNetwork rskMainnetCustom host=$BROWNIE_CUSTOM_HOST_MAINNET chainid=30 explorer=https://blockscout.com/rsk/mainnet/api

RUN mkdir /home/www-data && mkdir /home/www-data/app \
    && mkdir /home/www-data/app/price_feeder

ARG CONFIG=config.json

WORKDIR /home/www-data/app/price_feeder/
COPY engines/*.py ./engines/
COPY price_feeder.py ./
COPY price_engines.py ./
ADD $CONFIG ./config.json
ENV PATH "$PATH:/home/www-data/app/price_feeder/"
ENV PYTHONPATH "${PYTONPATH}:/home/www-data/app/price_feeder/"
CMD ["python", "./price_feeder.py"]
