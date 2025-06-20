import os
import secrets
import uuid
from fastapi import FastAPI, Header, Request, HTTPException, Depends
import hmac, hashlib, base64, time, json
import requests
from dotenv import load_dotenv
import uvicorn
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse, Response

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

data_dict = {
    "merchant_id": "merchant_0a9b0a0e-1d46-4762-9a5a-299eee3777bc",
    "api_key": "snd_JOdyV2vyuk5Hx8itpcB8or6OdTQLHnoSKp4GWdLMRpArQSaCg72UzQhpH9RvEbwK",
    "payment_response_hash_key": "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "profiles": [
        {"profile_id": "pro_Y58GwHnsyf9Uw09KTFbC", "merchant_connector_id": "mca_NyWXY56NjeJG6tyDd7Yp",
         "profile_name": "US_default"},
        {"profile_id": "pro_WOem7XduQBA8D6CqTqvT", "merchant_connector_id": "mca_Ms7jGE6DzZa4w6fULBg9",
         "profile_name": "Profile 1"},
        {"profile_id": "pro_NDmWdTYdJMOmdH2nZvMh", "merchant_connector_id": "mca_EXFgkObv3Ev7Wzk4fpc6",
         "profile_name": "Profile 2"},
        {"profile_id": "pro_7jAtP8hpv20vctRZDc1T", "merchant_connector_id": "mca_NLaMeRsID0HimfrTY1z9",
         "profile_name": "Profile 3"},
        {"profile_id": "pro_Wz1NCfSnkptsycR1WyDj", "merchant_connector_id": "mca_NEDTP5n3F1Ja0Ne6fdiT",
         "profile_name": "Profile 4"},
        {"profile_id": "pro_Th1mwfYRaYQesmPONvZy", "merchant_connector_id": "mca_4secqwnrCKyvThXA1jQV",
         "profile_name": "Profile 5"},
    ]
}
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
        "snd_qkhiSoxHT7gCuFxrYXbJl2wnuFR5XpwPxXamIQ9xnnmdV0rxYm3aeA3kAMdRHfXX",
    "merchant_53efbb2f-3b52-40a8-830c-f02dbca1ac0e":
        "dev_zCMn6i6CW51fznwjLuSZjCNmbrLm2XGtSuyhRLr2863gTmFPYHeaFeOQ8zLzfU62",
    "merchant_d34fd21d-953e-446a-8c65-a48bcb0a12b8":
        "dev_vxo5Kukmb2S1g8MHrARoT4OKoHduo4Q4HhWQs9XbYhfAB4VlwfHth6h0HFOYMcA8",
    "merchant_e022b3df-d020-4eb6-a798-937827617b75":
        "dev_PqMelDwV4wCiEMBbhTbSsm62Am17x8tYf0dS7Y8rGArOYC54CclU9YG2acXdIrd6",
    "merchant_331ab738-45be-4e62-ab9b-146fbc3ecda5":
        "dev_KycZWBwcTKZrpmTM2VsuM74YWzqFzwArL6lLGBgCtxu9OCIjwPHZpcuyVfNyjVlN",
    "merchant_6b10ed12-5e18-44f8-a7ea-89f483e23329":
        "snd_CQub4g5SD0MfW7aDFwsChsSKpCVKaTtlEvCr9WBunkxDbHNA6szVgUTRjPA42KqC",
    "merchant_f1fdab77-4fec-4188-aa4e-6d273ae372b0":
        "snd_tFe6mNuXEfWafPbdIwbNzpf89tOzkkBmS8DaCVshxwKKycsYbyjgXU3hMbAc785i",
    "merchant_1ee30a9f-9476-493e-a36a-a28fc1c185c4":
        "snd_c7hM3aenyya8fDN8PLdtzCZpiIGidqYxUced47LFQYfmyvaYQ4YaOhj52q8cP0Kn",
    "merchant_0da75e21-049e-462d-8f09-01e78cfe670c":
        "snd_iyWGk1ij3r4A4xQNBwnB8L3tguVOTs5AdMHOKr73F84ade5fBi863pLcki1OURHC",
    "merchant_6ed42cb7-2edb-426a-b968-865a33394dda":
        "snd_UpAyhr4ksBAEYuc4uptbAHRBhJmT22AsCxPrZWnGKl0ydEZj9ll24XM39iV7oDSc",
    "merchant_defd2a4b-587e-4807-9f2c-62f7383b2424":
        "snd_ODCt6TchezdiYWKVPVeSETZpOjE6Ko19qtuocG1tjLMNveDvBhRSsWg2ucaRagLa",
    "merchant_622d2eed-f556-4f42-a76c-3edb985771a3":
        "snd_OfGVX3PDM2U9q1HlsM7YbLdXqYK1wzyBNhqAl4V6LYGy8nM8o9or4fIoOXrDJLeU",
    "merchant_3a0695d7-7392-42c0-a39c-3b9472c70bed":
        "snd_cYf1sR6JQo37btx8wLP0GEGV54g8jni1wcW3HnMzj3bXs2MAwUaliiMZKhjNS92g",
    "merchant_18fda02f-2e10-48f5-bea6-d0deceee9cd5":
        "snd_IJSGHOHIuciVLRNCBZTMkBp6wjXCpv0VLu4YOsve0Tna7SNjlC6KimeeaBIXQAyf",
    "merchant_0a9b0a0e-1d46-4762-9a5a-299eee3777bc":
        "snd_JOdyV2vyuk5Hx8itpcB8or6OdTQLHnoSKp4GWdLMRpArQSaCg72UzQhpH9RvEbwK",
    "merchant_0062e33e-62db-4342-a873-c3f3b1a9c0ca":
        "snd_xbq45K4mwEclI8ht5YHSatiKJ7paFgvKT6VsvG3AlKqyw7qkNa97juUIX1IOxmjz",
    "merchant_d8453874-2faa-4ed0-8f8d-9cae553e60c2":
        "snd_48UiegaueusWlJVPvhbCgoDVrTCWrk3wa7LRZ4OdZup7rEKsn7sHSS2TW1BdWotN",
    "merchant_e6842cb0-39bd-4ff5-b03b-0b414e336a77":
        "snd_Ulgpdnl8U0HJSpR2KOsIgU4TadoRpd19sV9kp72fu8rD9GGAXX4dTG8Q10J7oU88",
    "merchant_82b6e5cb-9205-4f9c-88e1-7f40d1e82087":
        "snd_UCCApcRllvDjqp6vsbl3w12wpIfyKgPgHzPGTWkbzsefsvn1orTBnWyrDxPTA0Js",
    "merchant_5f3a497c-baab-414e-8f96-ad98c3e1add1":
        "snd_5Vl3SASXt9F5wh7EjpWREdwbkTY3LRYBKCeBA1msruDEZ0MKkrcsAMLJgXielbzy"
}

profile_response_hash_mapping = {
    "pro_WOem7XduQBA8D6CqTqvT":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "pro_NDmWdTYdJMOmdH2nZvMh":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "pro_7jAtP8hpv20vctRZDc1T":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "pro_Wz1NCfSnkptsycR1WyDj":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "pro_Th1mwfYRaYQesmPONvZy":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb",
    "pro_Y58GwHnsyf9Uw09KTFbC":
        "HTuaP9q2l2MHaZfHXi1EjNqtH9Z52SHscrNELg2aRw7flElF29ChNeMSjgpw4hCb"
}

connector_id_response_hash_key_mapping = {
    "pro_Y58GwHnsyf9Uw09KTFbC": "mca_NyWXY56NjeJG6tyDd7Yp",
    "pro_WOem7XduQBA8D6CqTqvT": "mca_Ms7jGE6DzZa4w6fULBg9",
    "pro_NDmWdTYdJMOmdH2nZvMh": "mca_EXFgkObv3Ev7Wzk4fpc6",
    "pro_7jAtP8hpv20vctRZDc1T": "mca_NLaMeRsID0HimfrTY1z9",
    "pro_Wz1NCfSnkptsycR1WyDj": "mca_NEDTP5n3F1Ja0Ne6fdiT",
    "pro_Th1mwfYRaYQesmPONvZy": "mca_4secqwnrCKyvThXA1jQV"
}
security = HTTPBasic()
admin_combined_headers = {**admin_api_key_headers, **content_type_headers}
# merchant_combined_headers = {**merchant_api_key_headers, **content_type_headers}
# API endpoints
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


@app.post("/create_payment_link", tags=["Payments"])
def create_payment_link(merchant_id: str, amount: int, profile_id: str):
    create_payment_link_request = f"{sandbox_endpoint}/payments"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
        "currency": "USD",
        "connector": ["stripe_test"],
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
        message = f"Failed to fetch payment methods - {response.text}"
        print(message)
        return {"message": message, "response": {}}


@app.get("/payments", tags=["Payments"])
def get_payments(merchant_id: str, payment_id: str = None, profile_id: str = None):
    """
    Get all payments for the merchant.
    """
    all_payments_request = f"{sandbox_endpoint}/payments/list"
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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
    merchant_api_key_headers = {"api-key": mapping.get(merchant_id, MERCHANT_API_KEY)}
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)


"""
Run all services:
docker compose --profile full_setup --profile scheduler --profile full_kv --profile clustered_redis --profile monitoring --profile olap up

FastAPI server:
python main.py or uvicorn main:app --reload --port 8005

Tunnel the server to the internet using ngrok:
ngrok http 8089
"""
#
