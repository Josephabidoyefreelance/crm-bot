from flask import Flask, request, jsonify
from process_incoming import handle_reply, update_lead_status

app = Flask(__name__)

@app.route("/incoming_sms", methods=["POST"])
def receive_sms():
    data = request.json
    text = data.get("text", "")
    lead_id = data.get("lead_id", "")
    current_status = data.get("current_status", None)

    reply_text, new_status = handle_reply(lead_id, text, current_status)

    if new_status:
        update_lead_status(lead_id, new_status)

    return jsonify({"status": "ok", "reply": reply_text})

if __name__ == "__main__":
    app.run(debug=True)
