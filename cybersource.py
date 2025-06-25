import requests

# events_url = "https://apitest.cybersource.com/notification-subscriptions/v1/products/bgfqwerty123_1749131358"
# events_response = requests.get(events_url)

webhook_subscription = "https://apitest.cybersource.com/notification-subscriptions/v1/webhooks"
webhook_subscription_payload = {
    "name": "Test Webhook Subscription",
    "description": "Sample Webhook from Developer Center",
    "organizationId": "bgfqwerty123_1749131358",
    "healthCheckUrl": "https://f3cf-103-81-118-114.ngrok-free.app/health",
    "webhookUrl": "https://f3cf-103-81-118-114.ngrok-free.app/webhooks/merchant_0a9b0a0e-1d46-4762-9a5a-299eee3777bc/mca_Ms7jGE6DzZa4w6fULBg9",
    "notificationScope": "SELF",
    "securityPolicy": {
        "securityType": "KEY",
    },

}
webhook_subscription_response = requests.post(webhook_subscription)
breakpoint()
