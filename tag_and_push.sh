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

# login into aws ecr
$(aws ecr get-login --no-include-email --region us-west-1)

docker tag moc_price_feeder_$ENV:latest 551471957915.dkr.ecr.us-west-1.amazonaws.com/moc_price_feeder_$ENV:latest
docker push 551471957915.dkr.ecr.us-west-1.amazonaws.com/moc_price_feeder_$ENV:latest