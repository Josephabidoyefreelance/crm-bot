def classify_reply(text, current_lead_status=None, current_workflow=None, property_address="1250 Larkin Ave"):
    """
    Classify the incoming SMS reply and decide:
    - What reply templates to send (list of strings)
    - What new lead status to set (or None)
    - Whether to resume workflow (True/False)

    Args:
      text (str): Incoming SMS text (lowercase recommended).
      current_lead_status (str): Current lead status label (optional).
      current_workflow (str): Current workflow name (optional).
      property_address (str): Property address for templated replies.

    Returns:
      dict with keys:
        - 'reply_templates': list of str templates to send as SMS replies (empty list = no reply)
        - 'new_status': new lead status to set (None = no change)
        - 'resume_workflow': bool, whether to resume the current workflow or not
    """
    text_lower = text.lower().strip()
    reply_templates = []
    new_status = None
    resume_workflow = False

    # Templates with placeholders
    identity_template = f"My name is Troy Golden, I am a commercial real estate broker. I help people sell properties like {property_address}. Can we have a call? Here's my website: https://goldengrouprealestateinc.com/"
    discuss_template = f"I wish to discuss my listing services and how I can help you sell properties like {property_address}"
    help_sell_template = f"I help people sell properties like {property_address}. Can we have a call? Here's my website: https://goldengrouprealestateinc.com"
    buyer_template = "Do you have a buyer? I have many active buyers looking for properties like yours."

    # === 1. Identity questions ===
    identity_keywords = ["who is this", "what company", "who are you", "what's your name", "identify yourself", "who is this?"]
    identity_match = any(k in text_lower for k in identity_keywords)

    # === 2. What want to discuss questions ===
    discuss_keywords = ["what do you want to talk about", "how can i help you", "what's up", "what's this about", "what do you want"]
    discuss_match = any(k in text_lower for k in discuss_keywords)

    # === 3. Combined identity + discuss ===
    combined_match = identity_match and discuss_match

    # === 4. Property sold indications ===
    sold_keywords = ["we sold the property", "we no longer own the property", "i sold it", "it's sold", "its sold", "property sold"]
    sold_match = any(k in text_lower for k in sold_keywords)

    # === 5. Soft disinterest in selling ===
    soft_no_keywords = ["we're not interested in selling", "not selling", "not for sale", "just looking for a tenant", "just leasing the property", "not interested in selling"]
    soft_no_match = any(k in text_lower for k in soft_no_keywords)

    # === 6. Disinterest in exclusive listing ===
    not_interested_keywords = [
        "we're selling the property ourselves", "we don't work with brokers", "bring me a buyer and i'll pay you a commission",
        "if you bring me a buyer i'll work with you", "not looking to list", "so go sell it then", "i'll pay you for any buyer you bring",
        "i'll pay you if you bring a buyer", "no exclusive listing", "don't list my property"
    ]
    not_interested_match = any(k in text_lower for k in not_interested_keywords)

    # === 7. Confirm ownership ===
    confirm_owner_keywords = ["yes", "yep", "i own that property", "maybe... what do you want", "how can i help you", "maybe what do you want"]
    confirm_owner_match = any(k in text_lower for k in confirm_owner_keywords)

    # === 8. Property listed with broker ===
    listed_broker_keywords = ["we're already working with a broker", "the property is listed", "please talk to my agent", "have a broker", "working with a broker", "listed with broker"]
    listed_broker_match = any(k in text_lower for k in listed_broker_keywords)

    # === 9. Property under contract ===
    under_contract_keywords = ["it's under contract", "its under contract", "in due diligence", "in escrow", "scheduled to close", "contract signed", "closing soon"]
    under_contract_match = any(k in text_lower for k in under_contract_keywords)

    # === 10. Maybe interested / price info (no reply or status change) ===
    # Check if text contains numbers or vague interest keywords
    maybe_keywords = ["might sell", "maybe", "depending on price", "interested", "possibly", "1.5 mil", "2 mil", "offer", "would sell"]
    contains_number = any(char.isdigit() for char in text_lower)
    maybe_match = any(k in text_lower for k in maybe_keywords)

    # === 11. Ask about buyer ===
    buyer_keywords = ["do you have a buyer", "you have someone that wants to buy the property", "have a buyer", "buyer in hand"]
    buyer_match = any(k in text_lower for k in buyer_keywords)

    # === 12. Wants to talk personally ===
    personal_talk_keywords = ["i have interest in selling", "yes please call", "call me", "talk to me", "want to talk", "i want to talk"]
    personal_talk_match = any(k in text_lower for k in personal_talk_keywords)

    # === 13. Workflow stopping responses - example: 'I have a broker already' ===
    workflow_stop_keywords = ["i have a broker already", "already have a broker", "working with a broker"]
    workflow_stop_match = any(k in text_lower for k in workflow_stop_keywords)

    # === Decision logic ===

    # 3. Combined identity + discuss
    if combined_match:
        reply_templates.append(help_sell_template)
        reply_templates.append(discuss_template)
        # Resume workflow if in those specific workflows
        if current_workflow and current_workflow.lower() in ['flbo 1', 'flbo 2', 'fsbo 1', 'fsbo 2', 'expired 1', 'expired 2']:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # 1. Identity only
    if identity_match and not discuss_match:
        reply_templates.append(identity_template)
        if current_workflow and current_workflow.lower() in ['flbo 1', 'flbo 2', 'fsbo 1', 'fsbo 2', 'expired 1', 'expired 2']:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # 2. Discuss only
    if discuss_match and not identity_match:
        reply_templates.append(discuss_template)
        if current_workflow and current_workflow.lower() in ['flbo 1', 'flbo 2', 'fsbo 1', 'fsbo 2', 'expired 1', 'expired 2']:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # 4. Property sold
    if sold_match:
        return {"reply_templates": [], "new_status": "Prevsold", "resume_workflow": False}

    # 5. Soft no selling
    if soft_no_match:
        return {"reply_templates": [], "new_status": "soft no", "resume_workflow": False}

    # 6. Not interested (no exclusive listing)
    if not_interested_match:
        return {"reply_templates": [], "new_status": "not interested", "resume_workflow": False}

    # 7. Confirm ownership
    if confirm_owner_match:
        reply_templates.append(help_sell_template)
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": False}

    # 8. Property listed with another broker
    if listed_broker_match:
        if current_lead_status == "Relisted 1":
            return {"reply_templates": [], "new_status": "Hi TEST, is still available for sale? -Troy, CRE Broker", "resume_workflow": False}
        else:
            return {"reply_templates": [], "new_status": "Hi TEST, following up about in . Has the property sold yet? -Troy Golden, CRE broker", "resume_workflow": False}

    # 9. Property under contract
    if under_contract_match:
        if current_lead_status == "Under Contract":
            return {"reply_templates": [], "new_status": "Under Contract 2", "resume_workflow": False}
        else:
            return {"reply_templates": [], "new_status": "Under Contract", "resume_workflow": False}

    # 10. Maybe interested / price info — no reply or status change
    if maybe_match or contains_number:
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

    # 11. Ask about buyer
    if buyer_match:
        reply_templates.append(buyer_template)
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": False}

    # 12. Wants to talk personally — no reply
    if personal_talk_match:
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

    # 13. Workflow stopping responses
    if workflow_stop_match:
        # For example, change status to 'ReListed 1'
        return {"reply_templates": [], "new_status": "ReListed 1", "resume_workflow": False}

    # Otherwise, no reply, no status change (needs personal attention)
    return {"reply_templates": [], "new_status": None, "resume_workflow": False}
