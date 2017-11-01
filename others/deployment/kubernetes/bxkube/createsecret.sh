export OAUTH_TOKEN=`bx iam oauth-tokens | awk 'FNR == 2 {print $3 " " $4}'`
export ORG_GUID=`bx iam org "Aruns Organization" --guid`
export ACCOUNT_ID = '96ee4d5ceb9116e5924ba4a883ca14c0'
curl -XPOST -H "Authorization: ${OAUTH_TOKEN}" -H "Organization: ${ORG_GUID}" -H "Account: ${ACCOUNT_ID}" https://registry.eu-gb.bluemix.net/api/v1/tokens?permanent=true

kubectl create secret docker-registry regsecret --docker-server=registry.eu-gb.bluemix.net --docker-username=token --docker-password=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1NDhmM2VhOS0xNDM0LTU0YTMtYTJkYi1hZGU3NWViMzhmYjYiLCJpc3MiOiJyZWdpc3RyeS5ibHVlbWl4Lm5ldCJ9.aCWIAp_pwwiFOZxEH7gQTbyx-TUI1jAOf-0KVTZgklU --docker-email=abalasu1@in.ibm.com