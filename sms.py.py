import requests
from requests.auth import HTTPBasicAuth

CLOSE_API_KEY = "api_06w69rXjp1F3KOQmaShZ70.0tlaMFy2JA1gZhudoFGPMF"  # Replace with your real key

def send_sms(phone_number, message, lead_id=None):
    url = "https://api.close.com/api/v1/activity/sms/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "to": phone_number,
        "body": message,
        "direction": "outgoing",
    }

    if lead_id:
        payload["lead_id"] = lead_id

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        auth=HTTPBasicAuth(CLOSE_API_KEY, '')
    )

    if response.status_code == 201:
        print(f"✅ Sent SMS to {phone_number} for lead {lead_id}")
    else:
        print(f"❌ Error sending SMS to {phone_number}: {response.text}")

    return response
