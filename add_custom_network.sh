if  [[ $APP_CONNECTION_NETWORK == http* ]] || [[ $APP_CONNECTION_NETWORK == https* ]] ;
then
    # Custom network through environment:
    # Old: export APP_CONNECTION_NETWORK=http://localhost:4444,31
    # New: export APP_CONNECTION_NETWORK=http://localhost:4444,80001,PolygonMumbai,https://mumbai.polygonscan.com/
    # Ex.: export APP_CONNECTION_NETWORK=https://rpc-mumbai.matic.today,80001,Polygon,https://mumbai.polygonscan.com/
    echo "Adding custom network ..."
    arrConn=(${APP_CONNECTION_NETWORK//,/ })
    brownie networks add ${arrConn[2]}Network rskCustomNetwork host=${arrConn[0]} chainid=${arrConn[1]} explorer=${arrConn[3]} timeout=180
fi