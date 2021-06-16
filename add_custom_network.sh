if  [[ $APP_CONNECTION_NETWORK == http* ]] || [[ $APP_CONNECTION_NETWORK == https* ]] ;
then
    echo "Adding custom network ..."
    arrConn=(${APP_CONNECTION_NETWORK//,/ })
    brownie networks add RskNetwork rskCustomNetwork host=${arrConn[0]} chainid=${arrConn[1]} explorer=https://blockscout.com/rsk/mainnet/api
fi