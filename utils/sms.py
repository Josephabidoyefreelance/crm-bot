from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# === CONFIG ===
CLOSE_API_KEY = os.getenv("CLOSE_API_KEY")
CLOSE_HEADERS = {
    "Authorization": f"Bearer {CLOSE_API_KEY}",
    "Content-Type": "application/json"
}

# Your Close.com sender phone number ID (replace with your actual sender phone number ID)
SENDER_PHONE_NUMBER_ID = "phon_isxT8ekvGEyc9VHa4n6GCHnjoLsJfCcro1lfVHwvel5"

# === KEYWORD RESPONSES ===
KEYWORD_RESPONSES = {
    "who": "Hi! This is Troy Golden, a commercial real estate broker. I specialize in helping property owners like you sell or lease their buildings.",
    "want": "Thanks for your reply! I’d like to talk briefly about your plans for the property. Are you open to discussing options?",
    "buyer": "I have many active buyers and investors looking for properties like yours. I'd be happy to share your property with them!",
}

# === GET SMS STATUS ID FUNCTION ===
def get_sms_status_id():
    # Fetch all SMS statuses, then return the ID for "sent" or "queued" status
    url = "https://api.close.com/api/v1/status/activity_sms/"
    resp = requests.get(url, headers=CLOSE_HEADERS)
    if resp.status_code == 200:
        statuses = resp.json().get("data", [])
        # Usually, "sent" status label is used
        for status in statuses:
            if status["label"].lower() == "sent":
                return status["id"]
        # fallback if "sent" not found
        if statuses:
            return statuses[0]["id"]
    print("⚠️ Warning: Could not get SMS status ID, messages might fail")
    return None

# === SEND SMS FUNCTION ===
def send_sms(contact_id, message):
    status_id = get_sms_status_id()
    if not status_id:
        print("❌ Cannot send SMS without valid status_id")
        return

    url = "https://api.close.com/api/v1/activity/sms/"
    payload = {
        "contact_id": contact_id,
        "body": message,
        "sender_phone_number_id": SENDER_PHONE_NUMBER_ID,
        "status": status_id,
        "direction": "outbound"
    }
    response = requests.post(url, headers=CLOSE_HEADERS, json=payload)
    if response.ok:
        print(f"✅ SMS sent successfully to contact {contact_id}")
    else:
        print(f"❌ Failed to send SMS: {response.status_code} - {response.text}")

# === UPDATE LEAD STATUS FUNCTION ===
def update_lead_status(lead_id, status_label):
    # Get all lead statuses and find matching ID for status_label
    url_status = "https://api.close.com/api/v1/status/lead/"
    resp_status = requests.get(url_status, headers=CLOSE_HEADERS)
    if resp_status.status_code != 200:
        print(f"❌ Failed to get lead statuses: {resp_status.status_code} - {resp_status.text}")
        return

    statuses = resp_status.json().get("data", [])
    match = next((s for s in statuses if s["label"].lower() == status_label.lower()), None)
    if not match:
        print(f"⚠️ Status '{status_label}' not found.")
        return

    url_update = f"https://api.close.com/api/v1/lead/{lead_id}/"
    resp_update = requests.put(url_update, headers=CLOSE_HEADERS, json={"status_id": match["id"]})
    if resp_update.ok:
        print(f"✅ Lead status updated to {status_label}")
    else:
        print(f"❌ Failed to update lead status: {resp_update.status_code} - {resp_update.text}")

# === WEBHOOK ROUTE ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    print("✅ Received webhook:", data)

    if data.get("object_type") == "activity.sms" and data.get("action") == "created":
        sms = data.get("object", {})
        # Only process inbound SMS
        if sms.get("direction") != "inbound":
            return jsonify({"status": "ignored"}), 200

        lead_id = sms.get("lead_id")
        contact_id = sms.get("contact_id")
        phone_number = sms.get("from")
        text_body = sms.get("body", "").lower()

        print(f"📩 SMS from {phone_number}: {text_body}")

        # Auto-reply to keywords
        for keyword, reply in KEYWORD_RESPONSES.items():
            if keyword in text_body:
                send_sms(contact_id, reply)
                break

        # Update lead status based on certain keywords
        if "sold" in text_body:
            update_lead_status(lead_id, "Prevsold")
        elif "not interested" in text_body:
            update_lead_status(lead_id, "Not Interested")

    return jsonify({"status": "processed"}), 200

@app.route('/webhook', methods=['GET'])
def test():
    return "Webhook is live", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
