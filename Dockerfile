FROM python:3.7

# Autor
LABEL maintainer='martin.mulone@moneyonchain.com'

RUN apt-get update && \
    apt-get install -y \
        locales \
        supervisor

RUN echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /home/www-data && mkdir /home/www-data/app \
    && mkdir /home/www-data/app/price_feeder \
    && mkdir /home/www-data/app/price_feeder/logs

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /home/www-data/app/price_feeder/
COPY build ./build
COPY price_feeder.py ./
COPY price_engines.py ./
COPY contracts_manager.py ./
COPY config.json ./
ENV PATH "$PATH:/home/www-data/app/price_feeder/"
ENV PYTHONPATH "${PYTONPATH}:/home/www-data/app/price_feeder/"
CMD ["/usr/bin/supervisord"]
