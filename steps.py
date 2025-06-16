steps = """
git clone --depth 1 --branch latest https://github.com/juspay/hyperswitch
cd hyperswitch

Service
cd hyperswitch
sudo docker compose -f docker-compose-development.yml up pg
sudo docker compose -f docker-compose-development.yml up redis-standalone
sudo docker compose -f docker-compose-development.yml up migration_runner
sudo docker compose -f docker-compose-development.yml up hyperswitch-server (time consuming)
sudo docker compose -f docker-compose-development.yml up hyperswitch-control-center

ifconfig
check for block having enp and get its inet and request using that IP

docker ps -a
go insider hyperswitch-server container
sudo docker exec -it <hyperswitch-server-container-id> bin/bash

apt install python3-pip
apt install python3-requests
apt install postgresql



api_key should be "test_admin" as mentioned in hyperswitch/config/docker_compose.toml




Change config/dashboard.toml 
[default.endpoints]
api_url="http://localhost:8080" 
to 
[default.endpoints]
api_url="http://172.24.0.57:8080"
in config/dashboard.toml 


Change docker-compose-development.yml


  hyperswitch-web-sdk:
    command: bash -c 'npm run re:build && npx run webpack serve --config webpack.dev.js --host 0.0.0.0'
      
      
  hyperswitch-web-sdk:
    command: bash -c 'npm run re:build && npx webpack serve --config webpack.dev.js --host 0.0.0.0'


Provide metadata field while creating payment connector. (and also merchant account)

The business details provided in the request should match the business details of the merchant account.

In adding payment connector, use api key as merchant api key, not the test_admin api key.

This Payment could not be refund because it has a status of requires_confirmation. The expected state is succeeded, partially_captured

"""



main_account_creation = """ 
Main account creation

# Request
curl -X POST http://localhost:8080/accounts   -H "Content-Type: application/json"   -H "api-key: test_admin"   -d '{
    "merchant_id": "master_merchant",
    "merchant_name": "Master Merchant",
    "return_url": "https://example.com/return",
    "merchant_details": {},
    "webhook_details": {},
    "primary_business_details": [
      { "country": "IN", "business": "ecommerce" }
    ]
  }'

# Response
{"merchant_id":"master_merchant","merchant_name":"Master Merchant","return_url":"https://example.com/return","enable_payment_response_hash":true,"payment_response_hash_key":"rbxB8chF4B1mkT4loykbWmf3JL2A5dczWJOkZHVeLjMzcdyRDp8TpRQyoKiDZNiF","redirect_to_merchant_with_http_post":false,"merchant_details":{"primary_contact_person":null,"primary_phone":null,"primary_email":null,"secondary_contact_person":null,"secondary_phone":null,"secondary_email":null,"website":null,"about_business":null,"address":null},"webhook_details":{"webhook_version":null,"webhook_username":null,"webhook_password":null,"webhook_url":null,"payment_created_enabled":null,"payment_succeeded_enabled":null,"payment_failed_enabled":null},"payout_routing_algorithm":null,"sub_merchants_enabled":false,"parent_merchant_id":null,"publishable_key":"pk_dev_04a5b46ec2b642a093f295e75030cd52","metadata":null,"locker_id":null,"primary_business_details":[{"country":"IN","business":"ecommerce"}],"frm_routing_algorithm":null,"organization_id":"org_5129R5ssoOuyNzaFiR0S","is_recon_enabled":false,"default_profile":"pro_rvyPD37oQsVvAKc95Kcr","recon_status":"not_requested","pm_collect_link_config":null,"product_type":"orchestration"}


# Sub merchants creation
curl -X POST http://localhost:8080/accounts \
  -H "Content-Type: application/json" \
  -H "api-key: test_admin" \
  -d '{
    "merchant_id": "child_001",
    "merchant_name": "Child Merchant 001",
    "merchant_details": {
      "primary_email": "child@example.com"
    },
    "primary_business_details": [
      { "country": "IN", "business": "retail" }
    ],
    "sub_merchants_enabled": false,
    "parent_merchant_id": "master_merchant"
  }'

# Response
{"merchant_id":"child_001","merchant_name":"Child Merchant 001","return_url":null,"enable_payment_response_hash":true,
"payment_response_hash_key":"8dHSzSZpOaAW9id0kDekK8VNZANo7KzcdOHK6Z0eUvL5wg9hSIYelhA8nXfpmXOC",
"redirect_to_merchant_with_http_post":false,"merchant_details":{"primary_contact_person":null,"primary_phone":null,"primary_email":"child@example.com","secondary_contact_person":null,"secondary_phone":null,"secondary_email":null,"website":null,"about_business":null,"address":null},"webhook_details":null,"payout_routing_algorithm":null,"sub_merchants_enabled":false,"parent_merchant_id":null,"publishable_key":"pk_dev_5a79c9dfb482485fb639eaf2a9f81ac9","metadata":null,"locker_id":null,"primary_business_details":[{"country":"IN","business":"retail"}],"frm_routing_algorithm":null,"organization_id":"org_QMZC78OfDdhuGpVtMWfi","is_recon_enabled":false,"default_profile":"pro_B6CsmngDx5jtQO0sJpGu","recon_status":"not_requested","pm_collect_link_config":null,"product_type":"orchestration"}


curl -X POST http://localhost:8080/accounts \
  -H "Content-Type: application/json" \
  -H "api-key: test_admin" \
  -d '{
    "merchant_id": "child_002",
    "merchant_name": "Child Merchant 002",
    "merchant_details": {
      "primary_email": "child2@example.com"
    },
    "primary_business_details": [
      { "country": "IN", "business": "retail" }
    ],
    "sub_merchants_enabled": false,
    "parent_merchant_id": "master_merchant"
  }'

{"merchant_id":"child_002","merchant_name":"Child Merchant 002","return_url":null,"enable_payment_response_hash":true,"payment_response_hash_key":"fc4lRDMea0nagee9HycgnqySLyVAolzfZFJifayImOTmwElkJZMLffktkx1ylw5f","redirect_to_merchant_with_http_post":false,"merchant_details":{"primary_contact_person":null,"primary_phone":null,"primary_email":"child2@example.com","secondary_contact_person":null,"secondary_phone":null,"secondary_email":null,"website":null,"about_business":null,"address":null},"webhook_details":null,"payout_routing_algorithm":null,"sub_merchants_enabled":false,"parent_merchant_id":null,"publishable_key":"pk_dev_45931a78a7a34de8b1824ce6f8c7c091","metadata":null,"locker_id":null,"primary_business_details":[{"country":"IN","business":"retail"}],"frm_routing_algorithm":null,"organization_id":"org_PUoBugrMT0ww71RRm5hB","is_recon_enabled":false,"default_profile":"pro_InsUZavU5GMwFX8fCNci","recon_status":"not_requested","pm_collect_link_config":null,"product_type":"orchestration"}


# Create API keys for sub merchants
curl -X POST http://localhost:8080/api_keys/child_001 \
  -H 'Content-Type: application/json' \
  -H 'api-key: test_admin' \
  -d '{
  "name": "Sandbox integration key",
  "description": "Key used by our developers to integrate with the sandbox environment",
  "expiration": "never"
}'

# Response 001
{"key_id":"dev_WDYLqvKeVFIY1Ygm6SyJ","merchant_id":"child_001","name":"Sandbox integration key","description":"Key used by our developers to integrate with the sandbox environment","api_key":"dev_Q3eSq4YySOKDe9GshZ92w3LsW7VsGYpAvuXXEAOZZFzdZUwTmrosgwdvILkHpFGO","created":"2025-06-09T13:51:26.022Z","expiration":"never"}root@617bfbe44649


curl -X POST http://localhost:8080/api_keys/child_002 \
  -H 'Content-Type: application/json' \
  -H 'api-key: test_admin' \
  -d '{
  "name": "Sandbox integration key",
  "description": "Key used by our developers to integrate with the sandbox environment",
  "expiration": "never"
}'

# Response 002
{"key_id":"dev_jdUvelXcPtSRwsif22A7","merchant_id":"child_002","name":"Sandbox integration key","description":"Key used by our developers to integrate with the sandbox environment","api_key":"dev_Loff5tb46JKBzoe1FokCN9rBK6r2gSNDXUl1hbUfzFN32nnQ0hKqPBRKjb9NZO16","created":"2025-06-09T13:57:26.400Z","expiration":"never"}


# List API keys for sub merchants
curl -X GET http://localhost:8080/api_keys/child_002/list \
  -H "Content-Type: application/json" \
  -H "api-key: test_admin"

# Response
[
    {
        "key_id": "dev_K3rXrEdjP0ZrJdijMlnp",
        "merchant_id": "child_002",
        "name": "Sandbox integration key",
        "description": "Key used by our developers to integrate with the sandbox environment",
        "prefix": "dev_WspK3omk",
        "created": "2025-06-09T13:50:11.718Z",
        "expiration": "never"
    },
    {
        "key_id": "dev_jdUvelXcPtSRwsif22A7",
        "merchant_id": "child_002",
        "name": "Sandbox integration key",
        "description": "Key used by our developers to integrate with the sandbox environment",
        "prefix": "dev_Loff5tb4",
        "created": "2025-06-09T13:57:26.400Z",
        "expiration": "never"
    }
]

# Retrieve API Key
curl -X GET http://localhost:8080/api_keys/child_002/dev_K3rXrEdjP0ZrJdijMlnp \
  -H "Content-Type: application/json" \
  -H "api-key: test_admin"
  
  
curl --request GET \
  --url http://localhost:8080/accounts/child_002 \
  --header 'api-key: test_admin'

"""
