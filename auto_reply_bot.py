import os
import requests
import time
import re
import json
from dotenv import load_dotenv

# Load API key and configs
load_dotenv()
CLOSE_IO_API_KEY = os.getenv("CLOSE_IO_API_KEY")
SENDER_PHONE_NUMBER_ID = "phon_isxT8ekvGEyc9VHa4n6GCHnjoLsJfCcro1lfVHwvel5"
POLL_INTERVAL = 60  # 1 minute

SEEN_MESSAGES_FILE = "seen_messages.json"

TEMPLATES = {
    "who_is_this": "Hi, this is Troy Golden, a commercial real estate broker. I help people sell properties like 1250 Larkin Ave. Can we have a call? Here's my website: https://goldengrouprealestateinc.com/",
    "what_do_you_want": "I wish to discuss my listing services and how I can help you sell properties like 1250 Larkin Ave.",
    "yes": "I help people sell properties like 1250 Larkin Ave. Can we have a call? Here's my website: https://goldengrouprealestateinc.com/",
    "do_you_have_a_buyer": "I don't currently have a buyer but I’m actively working to find one.",
}

RESUMABLE_WORKFLOWS = ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]

def load_seen_messages():
    try:
        with open(SEEN_MESSAGES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"messages": data}
            return data
    except:
        return {"messages": []}

def save_seen_messages(state):
    with open(SEEN_MESSAGES_FILE, "w") as f:
        json.dump(state, f)

def contains(text, *phrases):
    return any(p in text for p in phrases)

def classify_reply(text, current_status=None, current_workflow=None):
    text = text.lower().strip()
    result = {"reply_templates": [], "new_status": None, "resume_workflow": False}

    if re.search(r"who.*(what|how)|what.*who|how.*who", text):
        result["reply_templates"] = ["yes", "what_do_you_want"]
        return result

    if contains(text, "who is this", "what company", "who are you", "who are u", "who's this"):
        result["reply_templates"].append("who_is_this")
    if contains(text, "what do you want", "how can i help", "what's up", "what is this about"):
        result["reply_templates"].append("what_do_you_want")
    if contains(text, "sold", "no longer own", "i sold it", "it's sold", "it’s sold"):
        result["new_status"] = "Prevsold"
    if contains(text, "not interested", "not selling", "not for sale", "just leasing", "just looking for tenant"):
        result["new_status"] = "soft no"
    if contains(text, "selling it myself", "dont work with brokers", "bring me a buyer", "won’t list", "not listing", "won't list", "if you bring me a buyer", "i'll pay you for any buyer", "so go sell it then"):
        result["new_status"] = "not interested"
    if text in ["yes", "yep", "i own that property", "maybe", "i think so", "maybe… what do you want", "how can i help you"]:
        result["reply_templates"].append("yes")
    if contains(text, "already listed", "my agent", "have a broker", "talk to my broker"):
        result["new_status"] = "Relisted 2" if current_status == "Relisted 1" else "Relisted 1"
    if contains(text, "under contract", "in escrow", "due diligence", "closing soon", "contract signed", "scheduled to close"):
        result["new_status"] = "Under Contract 2" if current_status == "Under Contract" else "Under Contract"
    if re.match(r"^\$?\s?\d+[kmb]?$", text) or contains(text, "depending on price", "maybe depends", "depends on offer"):
        return {}
    if contains(text, "do you have a buyer", "have someone that wants to buy"):
        result["reply_templates"].append("do_you_have_a_buyer")
    if contains(text, "call me", "talk", "interested in selling", "yes please call"):
        return {}
    if result["reply_templates"] and current_workflow in RESUMABLE_WORKFLOWS:
        result["resume_workflow"] = True
    result["reply_templates"] = list(dict.fromkeys(result["reply_templates"]))
    return result

def get_unread_sms():
    url = "https://api.close.com/api/v1/activity/?_limit=50&activity_type=sms_received&direction=inbound"
    resp = requests.get(url, auth=(CLOSE_IO_API_KEY, ''))
    if resp.status_code != 200:
        print(f"❌ Failed fetching messages: {resp.status_code} {resp.text}")
        return []
    return resp.json().get("data", [])

def send_sms(lead_id, contact_id, sender_phone_number_id, body):
    if not sender_phone_number_id:
        print("⚠️ No valid sender_phone_number_id, skipping SMS.")
        return
    data = {
        "lead_id": lead_id,
        "contact_id": contact_id,
        "sender_phone_number_id": sender_phone_number_id,
        "text": body,
        "status": "outbox",
        "direction": "outbound",
        "local_phone": sender_phone_number_id
    }
    print(f"📨 Sending SMS to lead {lead_id}:\n→ {body}")
    resp = requests.post("https://api.close.com/api/v1/activity/sms/", auth=(CLOSE_IO_API_KEY, ''), json=data)
    if resp.status_code == 200:
        print(f"✅ SMS sent successfully.")
    else:
        print(f"❌ Failed to send SMS: {resp.status_code} {resp.text}")

def update_lead_status(lead_id, status_label):
    status_url = "https://api.close.com/api/v1/status/lead/"
    statuses_resp = requests.get(status_url, auth=(CLOSE_IO_API_KEY, ''))
    if statuses_resp.status_code != 200:
        print(f"❌ Failed to get lead statuses: {statuses_resp.status_code} {statuses_resp.text}")
        return
    match = next((s for s in statuses_resp.json().get("data", []) if s["label"].lower() == status_label.lower()), None)
    if not match:
        print(f"⚠️ Lead status '{status_label}' not found.")
        return
    url = f"https://api.close.com/api/v1/lead/{lead_id}/"
    resp = requests.put(url, auth=(CLOSE_IO_API_KEY, ''), json={"status_id": match["id"]})
    if resp.status_code == 200:
        print(f"✅ Lead {lead_id} status updated to '{status_label}'.")
    else:
        print(f"❌ Failed to update lead status: {resp.status_code} {resp.text}")

def test_api_key():
    print("🔑 Testing API Key...")
    resp = requests.get("https://api.close.com/api/v1/status/lead/", auth=(CLOSE_IO_API_KEY, ''))
    if resp.status_code == 200:
        print("✅ API Key is valid.")
    else:
        print(f"❌ API Key test failed: {resp.status_code} {resp.text}")

def run_auto_reply_bot():
    print("🤖 Bot running. Checking for new inbound messages every 1 minute...\n")
    state = load_seen_messages()

    while True:
        print("🕵️ Checking for new inbound messages...")
        messages = get_unread_sms()

        for msg in messages:
            msg_id = msg.get("id")
            if msg_id in state["messages"]:
                continue
            state["messages"].append(msg_id)

            if msg.get('_type') != "SMS" or msg.get('direction') != "inbound":
                continue

            lead_id = msg.get("lead_id")
            contact_id = msg.get("contact_id")
            text = msg.get("text", "").strip()
            current_status = msg.get("status_label")
            current_workflow = None

            if not all([lead_id, contact_id, text]):
                print("⚠️ Missing info. Skipping.")
                continue

            print(f"\n💬 Processing message from lead {lead_id}: '{text}'")
            result = classify_reply(text, current_status, current_workflow)
            print(f"🔍 Classification result: {result}")

            if result.get("reply_templates"):
                for template_key in result["reply_templates"]:
                    body = TEMPLATES.get(template_key)
                    if body:
                        send_sms(lead_id, contact_id, SENDER_PHONE_NUMBER_ID, body)
                        break  # Send only the first matched reply
            else:
                print("ℹ️ No templates matched. No reply sent.")

            if result.get("new_status"):
                update_lead_status(lead_id, result["new_status"])

            if result.get("resume_workflow"):
                print(f"🔁 Workflow should resume for lead {lead_id}")

        save_seen_messages(state)
        print("⏳ Sleeping for 1 minute...\n")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    test_api_key()
    run_auto_reply_bot()
