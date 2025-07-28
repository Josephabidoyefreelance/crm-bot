from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === CONFIG ===
CLOSE_API_KEY = "your_close_api_key"
CLOSE_HEADERS = {
    "Authorization": f"Bearer {CLOSE_API_KEY}",
    "Content-Type": "application/json"
}

# === SIMPLE KEYWORD RESPONSES ===
KEYWORD_RESPONSES = {
    "who": "Hi! This is Troy Golden, a commercial real estate broker. I specialize in helping property owners like you sell or lease their buildings.",
    "want": "Thanks for your reply! I’d like to talk briefly about your plans for the property. Are you open to discussing options?",
    "buyer": "I have many active buyers and investors looking for properties like yours. I'd be happy to share your property with them!",
}

# === CLOSE API ACTIONS ===
def update_lead_status(lead_id, status):
    url = f"https://api.close.com/api/v1/lead/{lead_id}/"
    response = requests.put(url, headers=CLOSE_HEADERS, json={"status_label": status})
    print("✅ Lead status updated:", status)
    return response.ok

def send_sms(contact_id, text):
    url = "https://api.close.com/api/v1/activity/sms/"
    payload = {
        "contact_id": contact_id,
        "body": text,
        "direction": "outbound"
    }
    response = requests.post(url, headers=CLOSE_HEADERS, json=payload)
    print("📤 SMS sent:", text)
    return response.ok

# === MAIN WEBHOOK HANDLER ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    print("✅ Received webhook:", data)

    if data.get("object_type") == "activity.sms" and data.get("action") == "created":
        sms = data.get("object", {})
        if sms.get("direction") != "inbound":
            return jsonify({"status": "ignored"}), 200

        lead_id = sms.get("lead_id")
        contact_id = sms.get("contact_id")
        phone_number = sms.get("from")
        text_body = sms.get("body").lower()

        print(f"📩 SMS from {phone_number}: {text_body}")

        # Simple keyword logic
        for keyword, reply in KEYWORD_RESPONSES.items():
            if keyword in text_body:
                send_sms(contact_id, reply)
                break

        # Example logic to change lead status
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
