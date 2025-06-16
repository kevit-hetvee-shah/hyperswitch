import os
import uuid
from pyexpat.errors import messages

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

load_dotenv()
app = FastAPI()

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
MERCHANT_API_KEY = os.environ.get("MERCHANT_API_KEY")
CYBERSOURCE_API_KEY = os.environ.get("CYBERSOURCE_API_KEY")
CYBERSOURCE_SHARED_SECRET = os.environ.get("CYBERSOURCE_SHARED_SECRET")
CYBERSOURCE_MERCHANT_ID = os.environ.get("CYBERSOURCE_MERCHANT_ID")

# headers
admin_api_key_headers = {"api-key": ADMIN_API_KEY}

content_type_headers = {"Content-Type": "application/json"}
mapping = {
    "merchant_b13834b8-79a6-41cf-aa35-625837a365b8":
        "dev_x2Nm7DYAmhiwH9vRyycOVZfM2ThHLJTnUBWqHFGzlAGGLuXleibLGo5X3CEMaexo",
    "merchant_591298df-44e9-4b9a-b331-e517cac5492c":
        "dev_DPa0EeUNg2hngeaEMp2P7JawXXikj8BYwn5DdInEW9asRJAEqMlo8Dxtgu7Yc1Ry",
    "merchant_a36990b3-1555-4bcb-8018-2040d376f82e":
        "dev_CM3IfbLAvS8QETewsHlSqgpW9rzm30rsyX9Rglr6fNCKcoWDnOHNd4tSP919DtrB",
    "merchant_c77a7ab7-c6ef-4189-b3dc-6bd4ad6d4113":
        "dev_3jbCHPzuK0ecnLXSjQbZPO3TjpPMIs1R79ONWOuoaZCvxny337qc1y62G3ry4GLT",
    "merchant_25941ceb-94b9-4348-8794-5885ef295cca":
        "snd_TBWf5U19FqXbWDGRXUoExV8XVoBO7VIihz5KNeUkA6MtRvGZdUwbOi0Vhxv6RlZ2",
    "merchant_1750056339": "snd_vL9nU4gGPe4lXQbbSlW3HIDcQUzcF9bHvV8dk4mwMO2dP7gcqMg9KZFgIswNS9ej",
    "merchant_15034d84-c6e2-49a8-94f4-2285af1936f2":
        "snd_qkhiSoxHT7gCuFxrYXbJl2wnuFR5XpwPxXamIQ9xnnmdV0rxYm3aeA3kAMdRHfXX"
}

admin_combined_headers = {**admin_api_key_headers, **content_type_headers}
# merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
# API endpoints
sandbox_endpoint = "http://172.24.0.57:8080"


@app.post("/onboard_merchant")
def onboard_merchant(merchant_name: str, primary_contact_person: str,
                     primary_phone: str,
                     primary_email: str,
                     website: str,
                     about_business: str,
                     city: str,
                     country: str,
                     zip_code: str,
                     state: str,
                     first_name: str,
                     last_name: str,
                     address_line1: str,
                     business_type: str,
                     address_line2: str = None,
                     address_line3: str = None,
                     secondary_contact_person: str = None,
                     secondary_phone: str = None,
                     secondary_email: str = None,
                     merchant_id: str = None,
                     metadata=None
                     ):
    """
    Onboard a merchant by creating an account and API keys.
    """
    if not merchant_id:
        merchant_id = f"merchant_{uuid.uuid4()}"
    merchant_payload = {
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "organization_id": "org_x4JM5dF0bV2BbBoLFZnk",
        "merchant_details": {
            "primary_contact_person": primary_contact_person,
            "primary_phone": primary_phone,
            "primary_email": primary_email,
            "secondary_contact_person": secondary_contact_person,
            "secondary_phone": secondary_phone,
            "secondary_email": secondary_email,
            "website": website,
            "about_business": about_business,
            "address": {
                "city": city,
                # "country": country,
                "country": "US",
                "line1": address_line1,
                "line2": address_line2,
                "line3": address_line3,
                "zip": zip_code,
                "state": state,
                "first_name": first_name,
                "last_name": last_name
            }
        },
        "primary_business_details": [{
            # "country": country,
            # "business": business_type,
            "country": "US",
            "business": "default"
        }],
        "metadata": metadata if metadata else {}
    }
    merchant_request = f"{sandbox_endpoint}/accounts"
    response = requests.post(merchant_request, json=merchant_payload, headers=admin_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Merchant account {merchant_id} created successfully."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to create merchant account: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/list_api_keys")
def list_api_keys(merchant_id: str):
    """
        List API keys for the merchant.
    """
    list_api_keys_request = f"{sandbox_endpoint}/api_keys/{merchant_id}/list"
    response = requests.get(list_api_keys_request, headers=admin_api_key_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"API keys for merchant {merchant_id} listed successfully."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to list API keys: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/generate_api_keys")
def generate_api_keys(merchant_id: str):
    """
        Generate API keys for the merchant.
    """
    create_api_keys_request = f"{sandbox_endpoint}/api_keys/{merchant_id}"
    api_key_payload = {
        "name": "Merchant Initial API Keys",
        "description": "Merchant keys for initial setup",
        "expiration": "never"
    }
    # headers
    response = requests.post(create_api_keys_request, json=api_key_payload, headers=admin_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"API keys for merchant {merchant_id} created successfully."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to create API keys: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    response = requests.get(f"{sandbox_endpoint}/health")
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = "Server is up and healthy."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = "Unable to reach the server or server is down."
        print(message)
        return {"message": message, "response": {}}


@app.post("/add_payment_connector")
def add_payment_connector(merchant_id: str):
    """
    Add a payment connector for the merchant.
    """
    add_connector_request = f"{sandbox_endpoint}/account/{merchant_id}/connectors"
    cybersource_connector_payload = {
        "profile_id": "pro_msluoF24g1CFtSoJOdRU",
        "connector_type": "payment_processor",
        "connector_name": "cybersource",
        "connector_account_details": {
            "auth_type": "SignatureKey",
            "api_key": f"{CYBERSOURCE_API_KEY}",
            "key1": f"{CYBERSOURCE_MERCHANT_ID}",
            "api_secret": f"{CYBERSOURCE_SHARED_SECRET}",
        },
        "test_mode": True,
        "disabled": False,
        "metadata": {},
        "payment_methods_enabled": [
            {
                "payment_method": "card",
                "payment_method_types": [
                    {
                        "payment_method_type": "credit",
                        "card_networks": ["Visa", "Mastercard"],
                        "minimum_amount": 1,
                        "maximum_amount": 68607706,
                        "recurring_enabled": True,
                        "installment_payment_enabled": True,
                        "accepted_currencies": {
                            "list": [
                                "USD",
                                "EUR",
                                "INR",
                                "XOF"
                            ],
                            "type": "enable_only"
                        },
                        "accepted_countries": {
                            "list": [
                                "FR",
                                "DE",
                                "IN"
                            ],
                            "type": "enable_only"
                        },
                    },
                    {
                        "payment_method_type": "debit",
                        "card_networks": ["Visa", "Mastercard"],
                        "minimum_amount": 1,
                        "maximum_amount": 68607706,
                        "recurring_enabled": True,
                        "installment_payment_enabled": True,
                        "accepted_currencies": {
                            "list": [
                                "USD",
                                "EUR",
                                "INR",
                                "XOF"
                            ],
                            "type": "enable_only"
                        },
                        "accepted_countries": {
                            "list": [
                                "FR",
                                "DE",
                                "IN"
                            ],
                            "type": "enable_only"
                        },
                    }
                ]
            }
        ],
        "business_country": "US",
        "business_label": "default"
    }
    connector_payload = cybersource_connector_payload
    # todo: add merchant API key to the headers, how
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    response = requests.post(add_connector_request, json=connector_payload, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Payment connector added successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to add payment connector: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/create_payment_link")
def create_payment_link(merchant_id: str, ):
    create_payment_link_request = f"{sandbox_endpoint}/payments"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    payment_payload = {"amount": 6540,
                       "currency": "USD",
                       "payment_link": True,
                       "return_url": "https:/hyperswitch.io",
                       "authentication_type": "three_ds",
                       "session_expiry": 9000,
                       "business_country": "US",
                       "payment_method": "card",
                       "business_label": "default",
                       "payment_method_data": {
                           "card": {
                               "card_number": "4242424242424242",
                               "card_exp_month": "12",
                               "card_exp_year": "25",
                               "card_holder_name": "John Doe",
                               "card_cvc": "123",
                               "card_network": "Visa",
                               "card_issuer": "TEST"
                           }
                       },
                       "payment_link_config": {
                           "theme": "#4E6ADD",
                           "logo": "https://hyperswitch.io/favicon.ico",
                           "seller_name": "HyperSwitch Inc.",
                           "sdk_layout": "accordion",
                           "display_sdk_only": False,
                           "hide_card_nickname_field": True,
                           "show_card_form_by_default": True,
                           "payment_button_text": "Proceed to Payment!",
                           "transaction_details": [
                               {
                                   "key": "Policy Number",
                                   "value": "297472368473924",
                                   "ui_configuration": {
                                       "position": 5,
                                       "is_key_bold": True,
                                       "is_value_bold": True
                                   }
                               }
                           ]
                       }
                       }
    response = requests.post(create_payment_link_request, json=payment_payload,
                             headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Payment Link created successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to create payment link: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/list_payment_methods")
def get_payment_methods():
    # client_secret = "pay_Y4jNqPhQWP5g8K3CNVuA_secret_6M8MHubnQICAZvMzPTe4"
    client_secret = "pay_vtDvliDykbQadBUNmq2r_secret_jhiz8JWH7nf0RMswaM70"
    payment_methods_request = f"{sandbox_endpoint}/account/payment_methods"
    publishable_key = "pk_snd_b1f4a2e0517b4a71a1af9cc894f75ffb"
    merchant_api_key_headers = {"api-key": publishable_key}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    params = {
        "client_secret": client_secret
    }
    response = requests.get(url=payment_methods_request, params=params,
                             headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = "Payment methods fetched successfully."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = "Failed to fetch payment methods"
        print(message)
        return {"message": message, "response": {}}


# @app.post("/create_business_profile")
# def create_business_profile(merchant_id: str, profile_name: str):
#     """
#     Create a business profile for the merchant.
#     """
#     create_profile_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile"
#     profile_payload = {
#         "profile_name": profile_name
#     }
#     response = requests.post(create_profile_request, json=profile_payload, headers="merchant_combined_headers")
#     print(f"RESPONSE: {response}")
#     if response.status_code == 200:
#         message = f"Business profile {profile_name} created successfully for merchant {merchant_id}."
#         print(message)
#         return {"message": message, "response": response.json()}
#     else:
#         message = f"Failed to create business profile: {response.text}"
#         print(message)
#         return {"message": message, "response": {}}
#
#
# @app.get("/list_business_profiles")
# def list_business_profiles(merchant_id: str):
#     """
#     List business profiles for the merchant.
#     """
#     list_profiles_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile"
#     response = requests.get(list_profiles_request, headers="merchant_combined_headers")
#     print(f"RESPONSE: {response}")
#     if response.status_code == 200:
#         message = f"Business profiles listed successfully for merchant {merchant_id}."
#         print(message)
#         return {"message": message, "response": response.json()}
#     else:
#         message = f"Failed to list business profiles: {response.text}"
#         print(message)
#         return {"message": message, "response": {}}
#
#
# @app.delete("/delete_business_profile")
# def delete_business_profile(merchant_id: str, profile_id: str):
#     """
#     Delete a business profile for the merchant.
#     """
#     delete_profile_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile/{profile_id}"
#     response = requests.delete(delete_profile_request, headers=admin_combined_headers)
#     print(f"RESPONSE: {response}")
#     if response.status_code == 200:
#         message = f"Business profile {profile_id} deleted successfully for merchant {merchant_id}."
#         print(message)
#         return {"message": message, "response": response.json()}
#     else:
#         message = f"Failed to delete business profile: {response.text}"
#         print(message)
#         return {"message": message, "response": {}}
#
#
#

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
