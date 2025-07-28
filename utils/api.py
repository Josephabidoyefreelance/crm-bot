# utils/api.py

def get_replies(limit=None):
    # Dummy function to simulate getting replies with optional limit
    print(f"get_replies() called with limit={limit}")
    
    # For testing, generate some dummy replies
    dummy_replies = [
        {"phone": "+1234567890", "message": "Yes, I'm interested.", "lead_id": "lead_1"},
        {"phone": "+1987654321", "message": "Not interested.", "lead_id": "lead_2"},
        {"phone": "+1029384756", "message": "Call me later.", "lead_id": "lead_3"},
        # add more dummy replies if needed
    ]
    
    if limit is not None:
        return dummy_replies[:limit]
    return dummy_replies


def update_lead_status(lead_id, new_status):
    # Dummy function to simulate updating lead status
    print(f"update_lead_status() called with lead_id={lead_id}, new_status={new_status}")

def log_event(event):
    # Dummy function to simulate logging an event
    print(f"log_event() called with event: {event}")

def get_lead_by_phone(phone):
    # Dummy function to simulate fetching a lead by phone number
    print(f"get_lead_by_phone() called with phone={phone}")
    return {"id": "dummy_lead_id"}
