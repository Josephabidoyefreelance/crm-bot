import os
import time
import json
import openai
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
CLOSEIO_API_KEY = os.getenv("CLOSEIO_API_KEY")
BASE_URL = "https://api.close.com/api/v1"

# Templates
TEMPLATES = {
    "who is this": "Hi, this is Troy Golden, a commercial real estate broker. I help property owners sell their properties.",
    "what do you want to talk about": "I'm reaching out to see if you're open to offers or planning to sell your property.",
    "yes": "Thanks for confirming. I’d like to share how I can help you sell.",
    "do you have a buyer": "Yes, I work with buyers actively searching for properties like yours."
}

# Keep track of last processed activity ID to avoid reprocessing
LAST_ACTIVITY_FILE = "last_activity.txt"

def get_last_processed_id():
    if not os.path.exists(LAST_ACTIVITY_FILE):
        return None
    with open(LAST_ACTIVITY_FILE, "r") as f:
        return f.read().strip()

def save_last_processed_id(activity_id):
    with open(LAST_ACTIVITY_FILE, "w") as f:
        f.write(activity_id)

# Fetch recent incoming SMS messages from Close.io
def fetch_incoming_sms():
    url = f"{BASE_URL}/activity/sms/?direction=incoming&sort=-date_created&limit=20"
    response = requests.get(url, auth=(CLOSEIO_API_KEY, ''))
    if response.status_code != 200:
        print("Failed to fetch SMS:", response.text)
        return []
    return response.json().get("data", [])

# Send SMS via Close.io
def send_sms(contact_id, body):
    url = f"{BASE_URL}/activity/sms/"
    data = {"contact_id": contact_id, "body": body}
    r = requests.post(url, json=data, auth=(CLOSEIO_API_KEY, ''))
    print("Sent SMS:", body) if r.ok else print("Failed to send SMS:", r.text)

# Update lead status
def update_status(lead_id, new_status):
    url = f"{BASE_URL}/lead/{lead_id}/"
    data = {"status_label": new_status}
    r = requests.put(url, json=data, auth=(CLOSEIO_API_KEY, ''))
    print(f"Updated status to {new_status}") if r.ok else print("Status update failed:", r.text)

# Resume workflow (mocked)
def resume_workflow(lead_id, workflow_name):
    print(f"Resuming workflow '{workflow_name}' for lead {lead_id} (stub)")

# OpenAI prompt and classification
def classify_reply(reply_text, current_status, current_workflow):
    prompt = f"""
You are a smart assistant for a real estate broker. Classify this reply.

Reply: "{reply_text}"
Status: {current_status}
Workflow: {current_workflow}

Output JSON:
{{
  "template_to_send": "yes" / "who is this" / "what do you want to talk about" / "do you have a buyer" / null,
  "lead_status_change": "Under Contract" / "Prevsold" / "Not owner" / "Soft no" / "Not interested" / "ReListed 1" / "ReListed 2" / null,
  "should_resume_workflow": true / false
}}
Only give JSON, no explanation.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return json.loads(response['choices'][0]['message']['content'])
    except Exception as e:
        print("OpenAI error:", e)
        return None

# Main processing loop
def process_replies():
    last_id = get_last_processed_id()
    messages = fetch_incoming_sms()

    for message in reversed(messages):  # process oldest to newest
        if message["id"] == last_id:
            continue

        contact_id = message.get("contact_id")
        lead_id = message.get("lead_id")
        body = message.get("text_body")
        lead_status = message.get("lead_status_label", "")
        workflow = "FSBO 1"  # You can fetch actual workflow from your data

        print(f"\nNew reply from contact {contact_id}: {body}")

        result = classify_reply(body, lead_status, workflow)
        if not result:
            print("Could not classify reply.")
            save_last_processed_id(message["id"])
            continue

        template = result["template_to_send"]
        status = result["lead_status_change"]
        resume = result["should_resume_workflow"]

        if template and template in TEMPLATES:
            send_sms(contact_id, TEMPLATES[template])

        if status:
            update_status(lead_id, status)
        elif resume:
            resume_workflow(lead_id, workflow)

        # Save last processed message ID
        save_last_processed_id(message["id"])

if __name__ == "__main__":
    print("🤖 Starting AI Auto-Responder for Close.io")
    while True:
        try:
            process_replies()
        except Exception as e:
            print("Error in processing:", e)
        time.sleep(15)  # Check every 15 seconds
