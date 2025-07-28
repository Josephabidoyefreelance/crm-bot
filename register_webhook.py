import requests

CLOSE_API_KEY = "api_0EGy0bKxb2gy8Mxp6Q8xEU.63jttk8josvYzeCIIA66O9"  # Your real Close API key
WEBHOOK_URL = "https://25328375516e.ngrok-free.app/webhook"     # Confirm your active ngrok URL

payload = {
    "url": WEBHOOK_URL,
    "enabled": True,
    "events": [
        {
            "object_type": "activity.sms",  # ✅ Listen for SMS messages
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
