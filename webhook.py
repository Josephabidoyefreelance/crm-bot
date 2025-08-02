from flask import Flask, request, jsonify
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

CLOSE_API_KEY = os.getenv("CLOSE_API_KEY")
CLOSE_HEADERS = {
    "Authorization": f"Bearer " + CLOSE_API_KEY,
    "Content-Type": "application/json"
}

TEMPLATES = {
    "who_is_this": "Hi! This is Troy Golden, a commercial real estate broker.",
    "what_do_you_want": "Thanks for your reply! I'd like to talk briefly about your property.",
    "yes_confirm": "Thanks for confirming you're the owner! How can I assist?",
    "do_you_have_buyer": "I have buyers looking for properties like yours. Happy to connect!",
}

def send_sms(contact_id, text):
    url = "https://api.close.com/api/v1/activity/sms/"
    payload = {
        "contact_id": contact_id,
        "body": text,
        "direction": "outbound"
    }
    r = requests.post(url, headers=CLOSE_HEADERS, json=payload)
    print("SMS sent:", r.status_code, r.text)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    print("Incoming webhook:", data)

    if data.get("object_type") != "activity.sms" or data.get("action") != "created":
        return jsonify({"status": "ignored"}), 200

    sms = data.get("object", {})
    if sms.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200

    contact_id = sms.get("contact_id")
    text = sms.get("body", "").lower()

    if "who" in text:
        send_sms(contact_id, TEMPLATES["who_is_this"])
    elif "what" in text:
        send_sms(contact_id, TEMPLATES["what_do_you_want"])
    elif "yes" in text or "i own" in text:
        send_sms(contact_id, TEMPLATES["yes_confirm"])
    elif "buyer" in text:
        send_sms(contact_id, TEMPLATES["do_you_have_buyer"])

    return jsonify({"status": "processed"}), 200

@app.route("/", methods=["GET"])
def home():
    return "Close Webhook is live ✅", 200

if __name__ == "__main__":
    app.run(debug=True)
