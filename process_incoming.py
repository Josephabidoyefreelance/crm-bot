import re
import os
import requests

# --- TEMPLATES ---
TEMPLATES = {
    "who_is_this": "Hi, this is Troy Golden, a commercial real estate broker.",
    "what_do_you_want": "I’m reaching out regarding the property you own. How can I help?",
    "yes": "Great! Thanks for confirming you own the property.",
    "do_you_have_a_buyer": "I don't currently have a buyer but I’m actively working to find one.",
}

# --- PATTERNS ---
patterns = {
    "who_is_this": re.compile(r"(who\s*is\s*this|what\s*company|who\s*are\s*you)", re.I),
    "what_do_you_want": re.compile(r"(what\s*do\s*you\s*want|what['’]?s\s*this\s*about|how\s*can\s*i\s*help|what['’]?s\s*up)", re.I),
    "yes_owner": re.compile(r"(yes|yep|i\s*own|correct\s*contact|that’s\s*me)", re.I),
    "sold": re.compile(r"(sold|we\s*sold|no\s*longer\s*own)", re.I),
    "soft_no": re.compile(r"(not\s*selling|not\s*interested|not\s*for\s*sale|just\s*leasing|just\s*looking\s*for\s*a\s*tenant)", re.I),
    "not_interested": re.compile(r"(selling\s*ourselves|don’t\s*work\s*with\s*brokers|no\s*exclusive|bring\s*me\s*a\s*buyer|i’ll\s*pay\s*you)", re.I),
    "relisted": re.compile(r"(already\s*working\s*with\s*a\s*broker|property\s*is\s*listed|have\s*a\s*broker|talk\s*to\s*my\s*agent)", re.I),
    "under_contract": re.compile(r"(under\s*contract|in\s*escrow|due\s*diligence|scheduled\s*to\s*close|closing\s*soon)", re.I),
    "buyer_question": re.compile(r"(do\s*you\s*have\s*a\s*buyer|you\s*have\s*someone\s*to\s*buy)", re.I),
    "want_to_talk": re.compile(r"(please\s*call|call\s*me|i\s*have\s*interest)", re.I),
    "price_only": re.compile(r"^\s*(\d+(?:\.\d+)?\s*(mil)?|maybe|depending\s*on\s*price)\s*$", re.I),
}

# --- MAIN LOGIC ---
def classify_reply(text, current_status=None):
    text = text.strip().lower()
    
    if patterns["who_is_this"].search(text) and patterns["what_do_you_want"].search(text):
        return {"reply_templates": [TEMPLATES["yes"], TEMPLATES["what_do_you_want"]], "new_status": None, "resume_workflow": True}
    if patterns["who_is_this"].search(text):
        return {"reply_templates": [TEMPLATES["who_is_this"]], "new_status": None, "resume_workflow": True}
    if patterns["what_do_you_want"].search(text):
        return {"reply_templates": [TEMPLATES["what_do_you_want"]], "new_status": None, "resume_workflow": True}
    if patterns["yes_owner"].search(text):
        return {"reply_templates": [TEMPLATES["yes"]], "new_status": None, "resume_workflow": True}
    if patterns["buyer_question"].search(text):
        return {"reply_templates": [TEMPLATES["do_you_have_a_buyer"]], "new_status": None, "resume_workflow": True}
    if patterns["sold"].search(text):
        return {"reply_templates": [], "new_status": "Prevsold", "resume_workflow": False}
    if patterns["soft_no"].search(text):
        return {"reply_templates": [], "new_status": "soft no", "resume_workflow": False}
    if patterns["not_interested"].search(text):
        return {"reply_templates": [], "new_status": "not interested", "resume_workflow": False}
    if patterns["relisted"].search(text):
        new_status = "ReListed 2" if current_status == "ReListed 1" else "ReListed 1"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}
    if patterns["under_contract"].search(text):
        new_status = "Under Contract 2" if current_status == "Under Contract" else "Under Contract"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}
    if patterns["want_to_talk"].search(text):
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}
    if patterns["price_only"].search(text):
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}
    
    return {"reply_templates": [], "new_status": None, "resume_workflow": False}

# --- STATUS UPDATER ---
def update_lead_status(lead_id, new_status):
    url = f"https://api.close.com/api/v1/lead/{lead_id}/"
    headers = {
        "Authorization": f"Bearer {os.getenv('CLOSE_API_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.put(url, json={"status": new_status}, headers=headers)
    print(f"Status updated to {new_status}: {response.status_code}")
    return response

# --- FULL HANDLER ---
def handle_reply(lead_id, text, current_status=None):
    result = classify_reply(text, current_status)
    first_reply = result["reply_templates"][0] if result["reply_templates"] else None
    return first_reply, result["new_status"]
