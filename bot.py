from flask import Flask, request, send_from_directory
import requests
import os

app = Flask(__name__)

# Environment Variables se tokens load karein
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "YOUR_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "YOUR_VERIFY_TOKEN")

# Function to send message
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=data)

# Favicon.ico request handle karein (taaki 404 error na aaye)
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Empty response with status 204 (No Content)

# Webhook verification ke liye
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403

# Messenger se aane wale messages handle karein
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            for event in messaging:
                if event.get("message"):
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]
                    send_message(sender_id, f"Bot: Aapne kaha '{message_text}'")
    return "Message Processed", 200

# Flask App ko run karein
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render ke liye PORT set karein
    app.run(host="0.0.0.0", port=port, debug=True)
