import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key securely from environment
CLOSE_API_KEY = os.getenv("CLOSE_IO_API_KEY")
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
