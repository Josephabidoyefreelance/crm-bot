from flask import Flask, request, jsonify
import sys
import os

# Allow importing other files in the same folder
sys.path.append(os.path.dirname(__file__))

from my_sms import send_sms
import process_incoming_reply

app = Flask(__name__)

@app.route('/incoming_sms', methods=['POST'])
def incoming_sms():
    try:
        raw_data = request.data.decode('utf-8')
        print(f"Raw request data: {raw_data}")

        data = request.get_json(force=True)
        print(f"Parsed JSON data: {data}")

        lead_id = data.get("lead_id") or data.get("leadId")
        message_text = data.get("text")
        phone = data.get("from")

        print(f"\n✅ Received SMS from {phone} (lead {lead_id}): {message_text}")

        response_text, new_status = process_incoming_reply.handle_reply(lead_id, message_text)

        if response_text:
            send_sms(lead_id, response_text)

        if new_status:
            process_incoming_reply.update_lead_status(lead_id, new_status)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error in /incoming_sms:", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000)
