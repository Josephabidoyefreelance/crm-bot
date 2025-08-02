import json
import openai

TEMPLATES = {
    "who_is_this": "Hi, this is Troy Golden, a commercial real estate broker.",
    "what_do_you_want": "I’m reaching out regarding the property you own. How can I help?",
    "yes": "Great! Thanks for confirming you own the property.",
    "do_you_have_a_buyer": "I don't currently have a buyer but I’m actively working to find one.",
}

def classify_reply(text):
    system_prompt = f"""
You are helping a commercial real estate broker respond to leads.
You will get incoming messages and return a JSON response like this:

{{
  "reply_templates": ["yes", "what_do_you_want"],
  "new_status": "Under Contract",
  "resume_workflow": true
}}

Use these templates when appropriate:
- "who_is_this": reply if the lead asks who you are or who you work for.
- "what_do_you_want": reply if the lead asks what you want or what this is about.
- "yes": reply if the lead confirms they own the property or says "yes".
- "do_you_have_a_buyer": reply if they ask whether you have a buyer.

Statuses to apply if clearly implied:
- "Prevsold"
- "soft no"
- "not interested"
- "ReListed 1"
- "ReListed 2"
- "Under Contract"
- "Under Contract 2"

Incoming text: "{text}"

ONLY return valid JSON with fields: reply_templates (list), new_status (string or null), resume_workflow (true or false)
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        print("OpenAI raw response:", content)
        return json.loads(content)
    except Exception as e:
        print(f"❌ GPT classification failed: {e}")
        return {"reply_templates": [], "new_status": None, "resume_workflow": False}

def classify_reply(text):
    # Dummy example for now
    return {"reply_templates": ["who_is_this"], "new_status": None, "resume_workflow": False}

if __name__ == "__main__":
    result = classify_reply("Who is this?")
    print(result)
