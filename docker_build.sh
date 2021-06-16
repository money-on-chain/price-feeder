#!/bin/bash

# exit as soon as an error happen
set -e

usage() { echo "Usage: $0 -e <environment> -c <config file> " 1>&2; exit 1; }

while getopts ":e:c:" o; do
    case "${o}" in
        e)
            e=${OPTARG}
             ((e == "moc-alphatestnet" || e == "moc-testnet" || e == "moc-mainnet" || e == "rdoc-testnet" || e == "rdoc-mainnet" || e == "eth-testnet" || e == "eth-mainnet"  )) || usage
            case $e in
                moc-alphatestnet)
                    ENV=$e
                    ;;
                moc-testnet)
                    ENV=$e
                    ;;
                moc-mainnet)
                    ENV=$e
                    ;;
                rdoc-testnet)
                    ENV=$e
                    ;;
                rdoc-mainnet)
                    ENV=$e
                    ;;
                eth-testnet)
                    ENV=$e
                    ;;
                eth-mainnet)
                    ENV=$e
                    ;;
                *)
                    usage
                    ;;
            esac
            ;;
        c)
            c=${OPTARG}
            CONFIG_FILE=$c
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ] || [ -z "${c}" ] ; then
    usage
fi


docker image build -t moc_price_feeder_$ENV -f Dockerfile --build-arg CONFIG=$CONFIG_FILE .
echo "Build done!"

