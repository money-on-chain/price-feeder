#!/bin/bash

# exit as soon as an error happen
set -e 

usage() { echo "Usage: $0 -e <environment>" 1>&2; exit 1; }

while getopts ":e:" o; do
    case "${o}" in
        e)
            e=${OPTARG}
             ((e == "test" || e == "moc-testnet" || e == "rrc20-mainnet" || e == "rrc20-testnet" || e == "moc-mainnet" )) || usage
            case $e in
                test)      
                    ENV=$e
                    ;;
                moc-testnet)      
                    ENV=$e
                    ;;
                moc-mainnet)      
                    ENV=$e
                    ;;
                rrc20-testnet)
                    ENV=$e
                    ;; 
                rrc20-mainnet)
                    ENV=$e
                    ;; 
                *)
                    usage
                    ;;
            esac
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ]; then
    usage
fi




cp ./version/$ENV/abi/*.json ./build/


docker image build -t moc_price_feeder_$ENV .