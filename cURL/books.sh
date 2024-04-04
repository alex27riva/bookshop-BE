source ./env

curl --silent -H "Accept: application/json" \
    --location $server/api/books | jq .
