steps = """
git clone --depth 1 --branch latest https://github.com/juspay/hyperswitch
cd hyperswitch

Service
cd hyperswitch
sudo docker compose -f docker-compose-development.yml up

ifconfig
check for block having enp and get its inet and request using that IP

api_key should be "test_admin" as mentioned in hyperswitch/config/docker_compose.toml




Change config/dashboard.toml's default endpoints and add payment_link
[default.endpoints]
api_url="http://172.24.0.57:8089"
in config/dashboard.toml 
[payment_link]
sdk_url = "http://localhost:9050/HyperLoader.js"


Change config/docker_compose.toml and add
[payment_link]
sdk_url = "http://localhost:9050/HyperLoader.js"


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
