from flask import Flask, request, jsonify
import requests
import os
import openai
import json

app = Flask(__name__)

CLOSE_API_KEY = os.getenv("CLOSE_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- TEMPLATES ---
TEMPLATES = {
    "who_is_this": "Hi, this is Troy Golden, a commercial real estate broker.",
    "what_do_you_want": "I’m reaching out regarding the property you own. How can I help?",
    "yes": "Great! Thanks for confirming you own the property.",
    "do_you_have_a_buyer": "I don't currently have a buyer but I’m actively working to find one.",
}

# --- Simple classify_reply example ---
def classify_reply(text, current_status=None, current_workflow=None):
    text = text.lower()
    if "who is this" in text or "what company" in text or "who are you" in text:
        return {"reply_templates": ["who_is_this"], "new_status": None, "resume_workflow": True}
    if "what do you want" in text or "what's this about" in text or "how can i help" in text or "what's up" in text:
        return {"reply_templates": ["what_do_you_want"], "new_status": None, "resume_workflow": True}
    if "yes" in text or "yep" in text or "i own" in text:
        return {"reply_templates": ["yes"], "new_status": None, "resume_workflow": True}
    if "do you have a buyer" in text or "you have someone that wants to buy" in text:
        return {"reply_templates": ["do_you_have_a_buyer"], "new_status": None, "resume_workflow": True}
    # Add more logic here based on your rules
    # For now, no reply and no status change
    return {"reply_templates": [], "new_status": None, "resume_workflow": False}

def send_sms_closeio(lead_id, to_number, message):
    url = "https://api.close.com/api/v1/message/"
    headers = {
        "Authorization": f"Bearer {CLOSE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "lead_id": lead_id,
        "to": to_number,
        "message": message,
        "message_type": "sms"
    }
    response = requests.post(url, json=data, headers=headers)
    return response

@app.route('/incoming_sms', methods=['POST'])
def incoming_sms():
    data = request.json.get('data', {})
    lead_id = data.get('lead_id')
    from_number = data.get('from')
    to_number = data.get('to')
    incoming_text = data.get('message')

    classification = classify_reply(incoming_text)

    new_status = classification.get("new_status")
    if new_status:
        update_lead_status(lead_id, new_status)

    replies = classification.get("reply_templates", [])
    for reply_key in replies:
        message = TEMPLATES.get(reply_key)
        if message:
            send_sms_closeio(lead_id, from_number, message)

    return jsonify({"status": "ok"})

def update_lead_status(lead_id, new_status):
    url = f"https://api.close.com/api/v1/lead/{lead_id}/"
    headers = {
        "Authorization": f"Bearer {CLOSE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.put(url, json={"status": new_status}, headers=headers)
    return response

if __name__ == "__main__":
    app.run(port=5000)
