echo $PRICE_FEEDER_CONFIG > /home/www-data/app/price_feeder/config.json
export AWS_DEFAULT_REGION=us-west-1
/usr/bin/supervisord