import requests

# Your Close API key here (keep it private!)
API_KEY = "api_2syo0UnYRkhah2CxWw9fxI.380io3msbLAsxh6EaqMl4B"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def delete_webhook(webhook_id):
    url = f"https://api.close.com/api/v1/webhook/{webhook_id}/"
    response = requests.delete(url, headers=HEADERS)
    if response.ok:
        print(f"✅ Successfully deleted webhook: {webhook_id}")
    else:
        print(f"❌ Failed to delete webhook: {webhook_id}, status: {response.status_code}")
        print("Response:", response.text)

def create_webhook(new_url):
    data = {
        "url": new_url,
        "events": ["activity.sms.created"]
    }
    response = requests.post("https://api.close.com/api/v1/webhook/", headers=HEADERS, json=data)
    if response.ok:
        webhook_info = response.json()
        print("✅ Created new webhook successfully:")
        print(webhook_info)
    else:
        print(f"❌ Failed to create webhook, status: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    old_webhook_id = "whsub_5DVojT0hIrl3808kBBnhS7"  # <-- Your old webhook ID here
    new_webhook_url = "https://f15f3534ada6.ngrok-free.app/webhook"  # <-- Your new webhook URL here

    delete_webhook(old_webhook_id)
    create_webhook(new_webhook_url)
