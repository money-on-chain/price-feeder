#!/bin/bash

# exit as soon as an error happen
set -e

usage() { echo "Usage: $0 -e <environment> -c <config file> -i <aws id> -r <aws region>" 1>&2; exit 1; }

while getopts ":e:c:i:r:" o; do
    case "${o}" in
        e)
            e=${OPTARG}
             ((e == "ars-rsk-testnet" || e == "ars-polygon-mumbai" || e == "bnb-testnet" || e == "moc-alphatestnet" || e == "moc-testnet" || e == "moc-mainnet" || e == "rdoc-testnet" || e == "rdoc-mainnet" || e == "eth-testnet" || e == "eth-mainnet" || e == "tether-testnet" || e == "tether-mainnet"  )) || usage
            case $e in
                bnb-testnet)
                    ENV=$e
                    ;;
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
                tether-testnet)
                    ENV=$e
                    ;;
                tether-mainnet)
                    ENV=$e
                    ;;
                ars-polygon-mumbai)
                    ENV=$e
                    ;;
                ars-rsk-testnet)
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
        i)
            i=${OPTARG}
            AWS_ID=$i
            ;;
        r)
            r=${OPTARG}
            AWS_REGION=$r
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ] || [ -z "${c}" ] || [ -z "${i}" ] || [ -z "${r}" ]; then
    usage
fi

docker image build -t moc_price_feeder_$ENV -f Dockerfile --build-arg CONFIG=$CONFIG_FILE .
echo "Build done!"

# login into aws ecr
$(aws ecr get-login --no-include-email --region $AWS_REGION)

echo "Logging to AWS done!"

docker tag moc_price_feeder_$ENV:latest $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/moc_price_feeder_$ENV:latest

docker push $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/moc_price_feeder_$ENV:latest


echo "Finish!"