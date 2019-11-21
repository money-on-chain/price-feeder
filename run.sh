#!/bin/bash
docker run  -d \
    --env-file=price_feeder.env \
    --env PK_SECRET=VALUE_PRIVATE_KEY \
    moc_price_feeder_rrc20-testnet