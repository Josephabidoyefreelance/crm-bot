def classify_reply(text, current_lead_status=None, current_workflow=None):
    """
    Classify the incoming text reply and decide:
    - What templates to send (list)
    - Whether to change lead status
    - Whether to resume workflow
    """

    text_lower = text.lower().strip()

    # Templates
    template_identity = "My name is Troy Golden, I am a commercial real estate broker. I help people sell properties like 1250 Larkin Ave. Can we have a call? Here's my website: https://goldengrouprealestateinc.com/"
    template_discuss = "I wish to discuss my listing services and how I can help you sell properties like 1250 Larkin Ave"
    template_help_sell = "I help people sell properties like 1250 Larkin Ave. Can we have a call? Here's my website: https://goldengrouprealestateinc.com"
    template_do_you_have_buyer = "I don’t currently have a buyer in hand, but I’m actively looking. Are you working with any buyers?"

    reply_templates = []
    new_status = None
    resume_workflow = False

    # 1. Identity questions
    identity_keywords = ["who is this", "what company", "who are you", "what's your name"]
    # 2. What want to discuss
    discuss_keywords = ["what do you want to talk about", "how can i help you", "what’s up", "what's this about", "what do you want"]

    # Helper checks
    def contains_any(text, keywords):
        return any(k in text for k in keywords)

    # Scenario 3: Combined identity + discuss
    identity_asked = contains_any(text_lower, identity_keywords)
    discuss_asked = contains_any(text_lower, discuss_keywords)

    # Scenario 4: sold property
    sold_keywords = ["we sold the property", "we no longer own the property", "i sold it", "it's sold", "its sold"]

    # Scenario 5: soft no selling
    soft_no_keywords = ["not interested in selling", "not selling", "not for sale", "just looking for a tenant", "just leasing the property"]

    # Scenario 6: no exclusive listing
    no_exclusive_keywords = [
        "we're selling the property ourselves", "we don't work with brokers",
        "bring me a buyer and i'll pay you a commission", "if you bring me a buyer i'll work with you, but i don't list my properties",
        "not looking to list but will consider offers", "so go sell it then", "i'll pay you for any buyer you bring"
    ]

    # Scenario 7: confirm ownership
    confirm_ownership_keywords = ["yes", "yep", "i own that property", "maybe", "how can i help you"]

    # Scenario 8: listed with broker
    listed_with_broker_keywords = ["we're already working with a broker", "the property is listed", "please talk to my agent", "have a broker"]

    # Scenario 9: under contract
    under_contract_keywords = ["it's under contract", "in due diligence", "in escrow", "scheduled to close", "contract signed", "closing soon"]

    # Scenario 10: maybe interested / price info
    maybe_keywords = ["maybe", "might sell", "depending on price"]
    # Additionally, check if text is mostly numeric (price)
    is_price = text_lower.replace('.', '', 1).replace('mil', '').replace('m', '').replace('$', '').strip().replace(',', '').isdigit()

    # Scenario 11: ask about buyer
    ask_buyer_keywords = ["do you have a buyer", "you have someone that wants to buy the property"]

    # Scenario 12: wants to talk personally
    wants_talk_keywords = ["i have interest in selling", "yes please call"]

    # Scenario 13: workflow stopping phrases
    workflow_stop_keywords = ["i have a broker already", "i have a broker"]

    # Start classification logic

    # Scenario 3 combined - check first to handle both identity & discuss
    if identity_asked and discuss_asked:
        reply_templates.append(template_help_sell)
        reply_templates.append(template_discuss)
        # No status change, resume workflow if in FLBO/FSBO/Expired workflows
        if current_workflow in ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # Scenario 1 - identity questions only
    if identity_asked and not discuss_asked:
        reply_templates.append(template_identity)
        if current_workflow in ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # Scenario 2 - discuss questions only
    if discuss_asked and not identity_asked:
        reply_templates.append(template_discuss)
        if current_workflow in ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # Scenario 4 - sold property
    if contains_any(text_lower, sold_keywords):
        new_status = "Prevsold"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}

    # Scenario 5 - soft no selling
    if contains_any(text_lower, soft_no_keywords):
        new_status = "soft no"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}

    # Scenario 6 - no exclusive listing
    if contains_any(text_lower, no_exclusive_keywords):
        new_status = "not interested"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}

    # Scenario 7 - confirm ownership
    if contains_any(text_lower, confirm_ownership_keywords):
        reply_templates.append(template_help_sell)
        if current_workflow in ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # Scenario 8 - listed with broker
    if contains_any(text_lower, listed_with_broker_keywords):
        if current_lead_status == "Relisted 1":
            new_status = "Hi TEST, is still available for sale? -Troy, CRE Broker"
        else:
            new_status = "Hi TEST, following up about in . Has the property sold yet? -Troy Golden, CRE broker"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}

    # Scenario 9 - under contract
    if contains_any(text_lower, under_contract_keywords):
        if current_lead_status == "Under Contract":
            new_status = "Under Contract 2"
        else:
            new_status = "Under Contract"
        return {"reply_templates": [], "new_status": new_status, "resume_workflow": False}

    # Scenario 10 - maybe interested / price info - no response or change
    if contains_any(text_lower, maybe_keywords) or is_price:
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

    # Scenario 11 - ask about buyer
    if contains_any(text_lower, ask_buyer_keywords):
        reply_templates.append(template_do_you_have_buyer)
        if current_workflow in ["FLBO 1", "FLBO 2", "FSBO 1", "FSBO 2", "Expired 1", "Expired 2"]:
            resume_workflow = True
        return {"reply_templates": reply_templates, "new_status": None, "resume_workflow": resume_workflow}

    # Scenario 12 - wants to talk personally
    if contains_any(text_lower, wants_talk_keywords):
        # No reply, no status change, no workflow resume — handled personally
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

    # Scenario 13 - workflow stopping phrases
    if contains_any(text_lower, workflow_stop_keywords):
        # No reply, but lead status needs to be changed (handle externally)
        # Here we don't reply or resume workflow; lead status logic external
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

    # Default: unknown scenarios, no reply, no status change
    return {"reply_templates": [], "new_status": None, "resume_workflow": False}


def run_tests():
    test_cases = [
        # Scenario 1: identity questions
        ("Who is this?", None, None),
        ("What company do you work for?", None, None),

        # Scenario 2: what want to discuss
        ("What do you want to talk about?", None, None),

        # Scenario 3: combined identity + discuss
        ("I own that property! Who are you sir!", None, "FLBO 1"),
        ("Who is this? What's up?", None, "FSBO 2"),

        # Scenario 4: sold property
        ("We sold the property last week.", None, None),

        # Scenario 5: soft no selling
        ("We're not interested in selling right now.", None, None),

        # Scenario 6: no exclusive listing
        ("We're selling the property ourselves.", None, None),

        # Scenario 7: confirm ownership
        ("Yes, I own that property", None, None),

        # Scenario 8: property listed with broker
        ("We're already working with a broker.", "Relisted 1", None),
        ("Please talk to my agent.", None, None),

        # Scenario 9: under contract
        ("It's under contract.", None, None),
        ("Contract signed, closing soon.", "Under Contract", None),

        # Scenario 10: maybe interested / price info
        ("1.5 mil", None, None),
        ("Maybe...", None, None),

        # Scenario 11: ask about buyer
        ("Do you have a buyer?", None, None),

        # Scenario 12: wants to talk personally
        ("Yes please call me.", None, None),

        # Scenario 13: workflow stopping
        ("I have a broker already.", None, None),

        # Unknown scenario
        ("Random message that needs personal attention.", None, None),
    ]

    for i, (text, lead_status, workflow) in enumerate(test_cases, 1):
        print(f"Test case {i}: '{text}'")
        result = classify_reply(text, current_lead_status=lead_status, current_workflow=workflow)
        print("  Reply templates:", result["reply_templates"])
        print("  New lead status:", result["new_status"])
        print("  Resume workflow:", result["resume_workflow"])
        print("-" * 50)


if __name__ == "__main__":
    run_tests()
