BLOCKED_NUMBERS = set()

def get_replies(limit=100):
    """
    Fetch incoming SMS replies.
    Replace this stub with actual API calls or DB fetch in production.
    """
    # Dummy data for testing
    return [{
        "contact_phone": "+1234567890",
        "body": "Who is this?",
        "lead_id": "lead123"
    }]

def classify_reply(message):
    """
    Simple message classifier that returns a reply template and optional new lead status.
    Extend this with your real NLP/classification logic.
    """
    if "who" in message.lower():
        return {
            "new_status": None,
            "reply_templates": ["This is Troy from CRE Brokerage."]
        }
    # Add more conditions here for classification if needed
    return {}

def update_lead_status(lead_id, new_status):
    """
    Update the lead status in your CRM.
    Replace this with actual API/database update.
    """
    print(f"Updating lead {lead_id} status to {new_status}")

def log_action(phone, action, details):
    """
    Log actions such as SMS sent, status updates, errors, etc.
    Replace this with proper logging or database audit.
    """
    print(f"Log: {phone} -> {action} ({details})")

def send_sms(phone, template, lead_id=None):
    """
    Send SMS to a phone number.
    Replace with actual SMS sending logic or call to your SMS module.
    """
    print(f"Sending SMS to {phone}: {template}")

def save_blocked_number(phone):
    """
    Save a phone number to the blocklist to avoid messaging again.
    """
    BLOCKED_NUMBERS.add(phone)
    print(f"Blocked {phone}")

def send_test_sms():
    """
    Function to send a test SMS (for manual testing).
    """
    print("Sending test SMS")

def process_incoming_replies(limit=100):
    """
    Main processing function to fetch and respond to incoming replies.
    """
    print(f"Processing {limit} incoming SMS replies...")
    try:
        replies = get_replies(limit=limit)
    except TypeError:
        replies = get_replies()

    if not replies:
        print("No replies found.")
        return

    for i, reply in enumerate(replies):
        print(f"\nDEBUG: Reply #{i+1} received:", reply)

        if not isinstance(reply, dict):
            print("WARNING: Reply is not a dictionary, skipping.")
            continue

        phone = reply.get("contact_phone") or reply.get("phone") or reply.get("from") or reply.get("sender")
        if not phone:
            print("WARNING: No phone number found in reply, skipping.")
            continue

        message = reply.get("body") or reply.get("message") or ""
        lead_id = reply.get("lead_id")

        classification = classify_reply(message) or {}
        print(f"Classified reply for {phone}: {classification}")

        new_status = classification.get("new_status")
        if new_status:
            update_lead_status(lead_id, new_status)
            log_action(phone, "status_update", new_status)

        reply_templates = classification.get("reply_templates")
        if reply_templates:
            if phone in BLOCKED_NUMBERS:
                print(f"Skipping blocked number: {phone}")
                continue

            for template in reply_templates:
                try:
                    send_sms(phone, template, lead_id)
                    log_action(phone, "sms_sent", template)
                except Exception as e:
                    print(f"SMS failed to {phone}: {e}")
                    if "opt-out" in str(e).lower():
                        save_blocked_number(phone)
                    log_action(phone, "sms_failed", str(e))

def handle_reply(lead_id, message_text):
    """
    Process a single incoming reply message and return response text and new lead status.
    Used by your Flask app for real-time replies.
    """
    classification = classify_reply(message_text) or {}
    reply_templates = classification.get("reply_templates") or []
    response_text = " ".join(reply_templates) if reply_templates else None
    new_status = classification.get("new_status")
    return response_text, new_status

if __name__ == "__main__":
    print("🚀 CRM Bot is starting...")
    print("==== CRM BOT MENU ====")
    print("1. Process incoming replies")
    print("2. Send test SMS manually")
    choice = input("Choose an option (1/2): ")

    if choice == "1":
        process_incoming_replies()
    elif choice == "2":
        send_test_sms()
    else:
        print("Invalid choice.")
