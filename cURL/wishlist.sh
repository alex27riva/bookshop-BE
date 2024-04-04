source ./env

curl --silent -H "Accept: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    --location $server/api/wishlist | jq .