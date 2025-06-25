import os
import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, Header, Request, HTTPException, Depends
import hmac, hashlib, base64, time, json
import requests
from dotenv import load_dotenv
import uvicorn
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, Response
from database import Base, get_db

load_dotenv()
app = FastAPI()

all_models = Base.classes.keys()
Payments = Base.classes.payment_attempt

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
CYBERSOURCE_API_KEY = os.environ.get("CYBERSOURCE_API_KEY")
CYBERSOURCE_SHARED_SECRET = os.environ.get("CYBERSOURCE_SHARED_SECRET")
CYBERSOURCE_MERCHANT_ID = os.environ.get("CYBERSOURCE_MERCHANT_ID")

# headers
admin_api_key_headers = {"api-key": ADMIN_API_KEY}

content_type_headers = {"Content-Type": "application/json"}

mapping = json.loads(open("mapping.json").read())
profile_response_hash_mapping = json.loads(open("profile_response_hash_mapping.json").read())
connector_id_response_hash_key_mapping = json.loads(open("connector_id_response_hash_key_mapping.json").read())
security = HTTPBasic()
admin_combined_headers = {**admin_api_key_headers, **content_type_headers}

sandbox_endpoint = "http://localhost:8089"


@app.post("/onboard_merchant", tags=["Merchants"])
def onboard_merchant(
        merchant_name: str = "Test Merchant",
        primary_contact_person: str = "ABC XYZ",
        primary_phone: str = "3485784543",
        primary_email: str = "abc@gmail.com",
        website: str = "abc.com",
        about_business: str = "Test Business",
        city: str = "Rajkot",
        country: str = "US",
        zip_code: str = "360009",
        state: str = "Gujarat",
        first_name: str = "Test",
        last_name: str = "User",
        address_line1: str = "ABC",
        business_type: str = "default",
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
        unique_id = uuid.uuid4()
        merchant_id = f"merchant_{str(unique_id).replace('-', '_')}"
    merchant_payload = {
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "organization_id": os.environ.get('ORGANIZATION_ID'),
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
                "country": country,
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
            "country": country,
            "business": business_type
        }],
        "metadata": metadata if metadata else {}
    }
    merchant_request = f"{sandbox_endpoint}/accounts"
    response = requests.post(merchant_request, json=merchant_payload, headers=admin_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Merchant account {merchant_id} created successfully."
        print(message)
        with open("profile_response_hash_mapping.json", "r+") as f:
            data = json.load(f)
            data[response.json().get("default_profile")] = response.json().get("payment_response_hash_key")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to create merchant account: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/list_api_keys", tags=["API Keys"])
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


@app.post("/generate_api_keys", tags=["API Keys"])
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
        with open("mapping.json", "r+") as f:
            data = json.load(f)
            data[merchant_id] = response.json().get("api_key")
            f.seek(0)
            json.dump(data, f, indent=4)
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


@app.post("/add_payment_connector", tags=["Payment Connector"])
def add_payment_connector(merchant_id: str, profile_id: str = None):
    """
    Add a payment connector for the merchant.
    """
    add_connector_request = f"{sandbox_endpoint}/account/{merchant_id}/connectors"
    cybersource_connector_payload = {
        "profile_id": profile_id,
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    response = requests.post(add_connector_request, json=connector_payload, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Payment connector added successfully for merchant {merchant_id}."
        print(message)
        with open("connector_id_response_hash_key_mapping.json", "r+") as f:
            data = json.load(f)
            data[profile_id] = response.json().get("merchant_connector_id")
            f.seek(0)
            json.dump(data, f, indent=4)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to add payment connector: {response.text}"
        print(message)
        return {"message": message, "response": {}}

@app.delete("/delete_payment_connector", tags=["Payment Connector"])
def delete_payment_connector(merchant_id: str, connector_id: str):
    """
    Delete a payment connector for the merchant.
    """
    delete_connector_request = f"{sandbox_endpoint}/account/{merchant_id}/connectors/{connector_id}"
    response = requests.delete(delete_connector_request, headers=admin_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Payment connector {connector_id} deleted successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to delete payment connector: {response.text}"
        print(message)
        return {"message": message, "response": {}}

@app.post("/create_payment_link", tags=["Payments"])
def create_payment_link(merchant_id: str, amount: int, profile_id: str):
    create_payment_link_request = f"{sandbox_endpoint}/payments"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    platform_fee = int(0.01 * amount)  # Assuming 1% platform fee
    transaction_fee = int(0.02 * amount)  # Assuming 2% transaction fee
    total_amount = int(amount + platform_fee + transaction_fee)

    payment_payload = {
        "profile_id": profile_id,
        "amount": int(total_amount),
        "amount_to_capture": total_amount,
        "description": "Payment for Black Full Length Cargo Pant",
        "metadata": {
            "platform_fee": platform_fee,
            "transaction_fee": transaction_fee
        },
        "connector": ["cybersource"],
        # "connector": ["cybersource", "bitpay","cashtocode", "stripe"],
        "currency": "USD",
        "payment_link": True,
        "return_url": "https:/hyperswitch.io",
        "authentication_type": "no_three_ds",
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
            "logo": "https://cdn.shopify.com/s/files/1/0070/7032/articles/how_20to_20start_20a_20clothing_20brand_40bcfec9-c4c3-4b50-8865-89933a6f5429.png?v=1749486608",
            "seller_name": "ABC Clothing Store",
            "sdk_layout": "accordion",
            "display_sdk_only": False,
            "hide_card_nickname_field": True,
            "show_card_form_by_default": True,
            "payment_button_text": "Proceed to Payment!",
            "background_image": {
                "url": "https://img.freepik.com/free-photo/abstract-blue-geometric-shapes-background_24972-1841.jpg",
                "position": "bottom",
                "size": "cover"
            },
            "transaction_details": [
                {
                    "key": "Type",
                    "value": "Black Full Length Cargo Pant",
                    "ui_configuration": {
                        "position": 1,
                        "is_key_bold": True,
                        "is_value_bold": True
                    }
                },
                {
                    "key": "Size",
                    "value": "S (28)",
                    "ui_configuration": {
                        "position": 2
                    }
                },
                {
                    "key": "Colour",
                    "value": "Black",
                    "ui_configuration": {
                        "position": 3
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
        message = f"Failed to fetch payment methods - {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/payments", tags=["Payments"])
def get_payments(merchant_id: str, payment_id: str = None, profile_id: str = None):
    """
    Get all payments for the merchant.
    """
    all_payments_request = f"{sandbox_endpoint}/payments/list"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    if payment_id:
        response = requests.get(f"{sandbox_endpoint}/payments/{payment_id}", params={"payment_id": payment_id},
                                headers=merchant_combined_headers)
    elif profile_id:
        response = requests.get(f"{sandbox_endpoint}/payments/profile/list",
                                headers={**merchant_combined_headers, **{"X-Profile-Id":
                                                                             profile_id}})
    else:
        response = requests.get(all_payments_request, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Payments listed successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to list payments: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/create_refund", tags=["Refund"])
def create_refund(merchant_id: str, payment_id: str):
    refund_request = f"{sandbox_endpoint}/refunds"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    refund_payload = {
        "payment_id": payment_id,
        # "amount": amount,
        "refund_type": "instant"
    }
    response = requests.post(refund_request, json=refund_payload, headers=merchant_combined_headers)
    # payment must have status succeeded, partially_captured
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = "Refund initiated successfully."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to initiate refund - {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/refunds", tags=["Refund"])
def get_all_refunds(merchant_id: str, payment_id: str = None):
    """
    Get all refunds for the merchant.
    """
    all_refunds_request = f"{sandbox_endpoint}/refunds/list"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    if payment_id:
        response = requests.post(all_refunds_request, json={"payment_id": payment_id},
                                 headers=merchant_combined_headers)
    else:
        response = requests.post(all_refunds_request, headers=merchant_combined_headers, json={})
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Refunds listed successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to list refunds: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/create_business_profile", tags=["Business Profile"])
def create_business_profile(merchant_id: str, profile_name: str):
    """
    Create a business profile for the merchant.
    """
    create_profile_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile"
    profile_payload = {
        "profile_name": profile_name
    }
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    response = requests.post(create_profile_request, json=profile_payload, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Business profile {profile_name} created successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to create business profile: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/list_business_profiles", tags=["Business Profile"])
def list_business_profiles(merchant_id: str):
    """
    List business profiles for the merchant.
    """
    list_profiles_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    response = requests.get(list_profiles_request, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Business profiles listed successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to list business profiles: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/update_business_profile", tags=["Business Profile"])
def update_business_profile(merchant_id: str, profile_id: str):
    """
    Update a business profile for the merchant.
    """
    update_profile_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile/{profile_id}"
    merchant_connector_id = connector_id_response_hash_key_mapping[profile_id]
    profile_payload = {
        "webhook_details": {
            "webhook_url": f"http://localhost:8089/webhooks/{merchant_id}/{merchant_connector_id}",
            # "webhook_username": "webhook_user",
            # "webhook_password": "webhook_pass",
            "webhook_version": "v1",
            "payment_created_enabled": True,
            "payment_succeeded_enabled": True,
            "payment_failed_enabled": True,
        }
    }
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id)}
    merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
    response = requests.post(update_profile_request, json=profile_payload, headers=merchant_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Business profile {profile_id} updated successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to update business profile: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.delete("/delete_business_profile", tags=["Business Profile"])
def delete_business_profile(merchant_id: str, profile_id: str):
    """
    Delete a business profile for the merchant.
    """
    delete_profile_request = f"{sandbox_endpoint}/account/{merchant_id}/business_profile/{profile_id}"
    response = requests.delete(delete_profile_request, headers=admin_combined_headers)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Business profile {profile_id} deleted successfully for merchant {merchant_id}."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to delete business profile: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/get_organization_merchants", tags=["Merchants"])
def get_organization_merchants():
    organization_merchants_request = f"{sandbox_endpoint}/accounts/list"
    organization_id = os.environ.get('ORGANIZATION_ID')
    params = {
        "organization_id": os.environ.get('ORGANIZATION_ID')
    }
    response = requests.get(organization_merchants_request, headers=admin_combined_headers, params=params)
    print(f"RESPONSE: {response}")
    if response.status_code == 200:
        message = f"Successfully fetched merchants for {organization_id} organization."
        print(message)
        return {"message": message, "response": response.json()}
    else:
        message = f"Failed to fetch merchants given organization: {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.post("/webhooks/{merchant_id}/{merchant_connector_id}")
async def hyperswitch_webhook(req: Request, merchant_id: str, merchant_connector_id: str):
    print("WEBHOOK RECEIVED")
    payload = await req.json()
    body = await req.body()
    signature = req.headers.get("x-webhook-signature-512")
    if not signature:
        raise HTTPException(400, "Missing signature")
    secret = b"HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb"
    print("PAYLOAD:", payload)
    print("SIGNATURE:", signature)
    print("BODY:", body)
    digest = hmac.new(secret, body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(digest, signature):
        raise HTTPException(400, "Invalid signature")
    return {"status": "ok"}


@app.get("/")
def home():
    return RedirectResponse("/docs")

"""
import jwt

JWT_SECRET = "secret"
JWT_ALGORITHM = "HS256"


@app.post("/analytics", tags=["Analytics"])
def analytics():
    payload = {
        "user_id": "c7353da9-2a86-47d5-abde-5eede48bfed3",
        "merchant_id": "merchant_0a9b0a0e-1d46-4762-9a5a-299eee3777bc",
        "role_id": "org_admin",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "org_id": "org_GDkwz29PpqlZzdeLRM11",
        "profile_id": "pro_Y58GwHnsyf9Uw09KTFbC",
        "tenant_id": "public"
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "QueryType": "SingleStat",
        "X-Merchant-Id": payload["merchant_id"],
        "X-Profile-Id": payload["profile_id"],
        "api-key": "hyperswitch",
        "authorization": f"Bearer {token}"
    }

    payload_data = [
        {
            "timeRange": {
                "startTime": "2025-06-16T18:30:00Z",
                "endTime": "2025-06-24T07:18:49Z"
            },
            "mode": "ORDER",
            "source": "BATCH",
            "metrics": [
                "payment_success_rate",
                "payment_count",
                "payment_success_count",
                "connector_success_rate"
            ],
            "delta": True
        }
    ]

    response = requests.post(
        "http://localhost:8089/analytics/v1/org/metrics/payments",
        headers=headers,
        json=payload_data
    )

"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

"""
Run all services:
docker compose --profile full_setup --profile scheduler --profile full_kv --profile clustered_redis --profile monitoring --profile olap up

FastAPI server:
python main.py or uvicorn main:app --reload --port 8005

Tunnel the server to the internet using ngrok:
ngrok http 8089

FRM (Fraud Risk Management) Connector Issues
Webhooks Stop Due to FRM Failing, Not Just Deletion
Once FRM fails during the post-auth step:
 - Hyperswitch halts the flow.
 - It doesn’t progress to webhook dispatch.
Deleting or disabling the FRM connector doesn’t automatically resume normal flow—Hyperswitch may still be in a “stuck” state.

Remove and restart Hyperswitch thoroughly after disabling FRM

Use Riskified only, avoiding Signifyd until FRM HTTP errors are resolved.
Or wait for a patch release from Hyperswitch that addresses the 303 bug for Signifyd.
"""
#
