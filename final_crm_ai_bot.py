import os
import time
import json
import requests
import openai
from dotenv import load_dotenv

# Load your API keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
CLOSEIO_API_KEY = os.getenv("CLOSEIO_API_KEY")
BASE_URL = "https://api.close.com/api/v1"

# Make sure keys are loaded
print("OpenAI key loaded:", openai.api_key is not None)
print("Close.io key loaded:", CLOSEIO_API_KEY is not None)

# Templates to send
TEMPLATES = {
    "who is this": "Hi, this is Troy Golden, a commercial real estate broker. I help property owners sell their properties.",
    "what do you want to talk about": "I'm reaching out to see if you're open to offers or planning to sell your property.",
    "yes": "Thanks for confirming. I’d like to share how I can help you sell.",
    "do you have a buyer": "Yes, I work with buyers actively searching for properties like yours."
}

LAST_FILE = "last_sms_id.txt"

def get_last_processed_id():
    if os.path.exists(LAST_FILE):
        return open(LAST_FILE).read().strip()
    return None

def save_last_processed_id(i):
    with open(LAST_FILE, "w") as f:
        f.write(i)

def fetch_sms():
    resp = requests.get(f"{BASE_URL}/activity/sms/?direction=incoming&sort=-date_created&limit=20",
                        auth=(CLOSEIO_API_KEY, ''))
    if resp.status_code != 200:
        print("Failed to fetch SMS:", resp.text)
        return []
    return resp.json().get("data", [])

def send_sms(contact_id, body):
    r = requests.post(f"{BASE_URL}/activity/sms/",
                      json={"contact_id": contact_id, "body": body},
                      auth=(CLOSEIO_API_KEY, ''))
    print("SMS sent" if r.ok else "SMS send failed:", r.text)

def update_status(lead_id, status):
    r = requests.put(f"{BASE_URL}/lead/{lead_id}/", json={"status_label": status},
                     auth=(CLOSEIO_API_KEY, ''))
    print(f"Status {status} updated" if r.ok else "Status update failed:", r.text)

def resume_workflow(lead_id, wf):
    print(f"Resuming workflow '{wf}' for lead {lead_id} (placeholder)")

def classify_reply(text, status, workflow):
    prompt = f"""
Contact reply: "{text}"
Current status: {status}
Current workflow: {workflow}

Return ONLY JSON like:
{{
 "template_to_send": string or null,
 "lead_status_change": string or null,
 "should_resume_workflow": true or false
}}

Based on these rules:
- Ask who you are → template "who is this"
- Ask what you want → template "what do you want to talk about"
- Confirm owner → template "yes"
- Ask if you have a buyer → template "do you have a buyer"
- If sold → status "Prevsold"
- Soft no selling → status "Soft no"
- Broker-only interest → status "Not interested"
- Listed already → "ReListed 1" or "ReListed 2"
- Under contract → "Under Contract" or "Under Contract 2"
- Otherwise, no action
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return json.loads(resp['choices'][0]['message']['content'])
    except Exception as e:
        print("OpenAI error:", e)
        return None

def process():
    last_id = get_last_processed_id()
    messages = fetch_sms()
    if not messages:
        return last_id

    for msg in reversed(messages):
        if msg["id"] == last_id:
            continue

        contact_id = msg.get("contact_id")
        lead_id = msg.get("lead_id")
        body = msg.get("text_body", "")
        status = msg.get("lead_status_label", "")
        workflow = msg.get("status_label") or ""

        print("\n📩 New message:", body)
        result = classify_reply(body, status, workflow)
        print("Classification result:", result)

        if result:
            tmpl = result.get("template_to_send")
            new_stat = result.get("lead_status_change")
            resume = result.get("should_resume_workflow", False)

            if tmpl in TEMPLATES:
                send_sms(contact_id, TEMPLATES[tmpl])
            if new_stat:
                update_status(lead_id, new_stat)
            elif resume:
                resume_workflow(lead_id, workflow)

        last_id = msg["id"]

    save_last_processed_id(last_id)
    return last_id

if __name__ == "__main__":
    print("🤖 CRM AI Responder started.")
    while True:
        process()
        time.sleep(15)
