from flask import Flask, request, jsonify
import os
import openai
import json
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLOSE_API_KEY = os.getenv("CLOSE_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Templates used internally
TEMPLATES = {
    "who_is_this": "Hi, this is Troy Golden, a commercial real estate broker.",
    "what_do_you_want": "I’m reaching out regarding the property you own. How can I help?",
    "yes": "Great! Thanks for confirming you own the property.",
    "do_you_have_a_buyer": "I don't currently have a buyer but I’m actively working to find one.",
}

def classify_reply(text, current_status=None, current_workflow=None):
    system_prompt = f"""
You are an assistant helping a CRE broker. For an incoming message, return ONLY valid JSON with keys:
reply_templates (list of keys from {list(TEMPLATES.keys())}),
new_status (string or null),
resume_workflow (true or false).
Incoming text: "{text}"
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.3
        )
        return json.loads(resp.choices[0].message.content.strip())
    except Exception as e:
        print("GPT classification error:", e)
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

def send_sms_closeio(lead_id, to_number, message):
    res = requests.post(
        "https://api.close.com/api/v1/message/",
        json={"lead_id": lead_id, "to": to_number, "message": message, "message_type": "sms"},
        headers={"Authorization": f"Bearer {CLOSE_API_KEY}", "Content-Type": "application/json"}
    )
    print(f"Sent reply to {to_number}: {res.status_code}")
    return res

def update_lead_status(lead_id, new_status):
    res = requests.put(
        f"https://api.close.com/api/v1/lead/{lead_id}/",
        json={"status": new_status},
        headers={"Authorization": f"Bearer {CLOSE_API_KEY}", "Content-Type": "application/json"}
    )
    print(f"Updated lead {lead_id} to {new_status}: {res.status_code}")
    return res

@app.route('/incoming_sms', methods=['POST'])
def incoming_sms():
    payload = request.get_json(force=True)
    data = payload.get("data", payload)  # handle nested or flat structure
    lead_id = data.get("lead_id")
    from_number = data.get("from")
    incoming_text = data.get("message") or data.get("text")

    classification = classify_reply(incoming_text)
    if classification.get("new_status"):
        update_lead_status(lead_id, classification["new_status"])

    for key in classification.get("reply_templates", []):
        msg = TEMPLATES.get(key)
        if msg:
            send_sms_closeio(lead_id, from_number, msg)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
