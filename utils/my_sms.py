import requests
import base64

# Your Close.com API key here
API_KEY = "api_06w69rXjp1F3KOQmaShZ70.0tlaMFy2JA1gZhudoFGPMF"

# Encode API key for Basic Auth
AUTH_HEADER = base64.b64encode(f"{API_KEY}:".encode("ascii")).decode("ascii")

# Your verified Close.com phone number (sender)
FROM_NUMBER = "+16303948164"

def send_sms(to_phone, text, lead_id=None):
    """
    Send SMS via Close.com API.

    Parameters:
    - to_phone: recipient phone number (string)
    - text: message text to send (string)
    - lead_id: optional lead ID (string)
    """
    sms_data = {
        "from": FROM_NUMBER,
        "to": to_phone,
        "remote_phone": to_phone,
        "text": text,
        "status": "sent"
    }

    if lead_id:
        sms_data["lead_id"] = lead_id

    response = requests.post(
        "https://api.close.com/api/v1/activity/sms/",
        headers={
            "Authorization": f"Basic {AUTH_HEADER}",
            "Content-Type": "application/json"
        },
        json=sms_data
    )

    if response.status_code in [200, 201]:
        print(f"✅ SMS sent successfully to {to_phone}")
    else:
        print(f"❌ Error sending SMS to {to_phone}: {response.status_code} - {response.text}")
