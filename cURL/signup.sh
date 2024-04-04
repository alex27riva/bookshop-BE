source ./env

curl --silent -H "Accept: application/json" \
    --request POST \
    -H "Authorization: Bearer $TOKEN" \
    --location $server/api/signup | jq .