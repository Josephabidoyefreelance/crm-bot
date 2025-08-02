import requests

CLOSE_API_KEY = "api_2syo0UnYRkhah2CxWw9fxI.380io3msbLAsxh6EaqMl4B"
WEBHOOK_URL = "https://f15f3534ada6.ngrok-free.app/webhook"

payload = {
    "url": WEBHOOK_URL,
    "enabled": True,
    "events": [
        {
            "object_type": "activity.sms",
            "action": "created"
        }
    ]
}

response = requests.post(
    "https://api.close.com/api/v1/webhook/",
    auth=(CLOSE_API_KEY, ""),
    json=payload
)

print("Status Code:", response.status_code)
print("Response:", response.json())
