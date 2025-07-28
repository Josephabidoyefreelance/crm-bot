def get_replies(limit=100):
    print(f"get_replies() called with limit={limit}")
    # Dummy replies with expected keys
    return [
        {"contact_phone": "+1234567890", "reply_text": "Yes, I'm interested"},
        {"contact_phone": "+1987654321", "reply_text": "No thanks"},
        {"contact_phone": "+1122334455", "reply_text": "Call me later"},
    ]

def update_lead_status(lead_id, new_status):
    print(f"update_lead_status() called with lead_id={lead_id}, new_status={new_status}")

def log_event(event):
    print(f"log_event() called with event: {event}")

def get_lead_by_phone(phone):
    print(f"get_lead_by_phone() called with phone={phone}")
    return {"id": "dummy_lead_id"}
