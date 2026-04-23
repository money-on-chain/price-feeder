FROM python:3.12-slim

LABEL maintainer='martin.mulone@moneyonchain.com'

RUN apt-get update && \
    apt-get install -y --no-install-recommends locales tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo $TZ > /etc/timezone && \
    rm -f /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Use system malloc so freed memory is returned to the OS.
# pymalloc (default) holds 256KB arenas forever, causing slow RSS growth in ECS.
ENV PYTHONMALLOC=malloc

# Cap glibc arena count to prevent per-thread arena fragmentation.
ENV MALLOC_ARENA_MAX=2

# Flush stdout/stderr immediately so ECS CloudWatch Logs captures all output.
ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1

RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --no-create-home appuser

COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt

RUN mkdir -p /home/www-data/app/price_feeder && \
    chown -R appuser:appuser /home/www-data/app

ARG CONFIG=config.json

WORKDIR /home/www-data/app/price_feeder/
COPY --chown=appuser:appuser app_run_price_feeder.py ./
COPY --chown=appuser:appuser $CONFIG ./config.json
COPY --chown=appuser:appuser price_feeder/ ./price_feeder/

ENV AWS_DEFAULT_REGION=us-west-1
ENV PATH="$PATH:/home/www-data/app/price_feeder/"
ENV PYTHONPATH="/home/www-data/app/price_feeder/"

USER appuser

CMD [ "python", "./app_run_price_feeder.py" ]
