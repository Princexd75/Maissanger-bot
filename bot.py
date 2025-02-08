from flask import Flask, request
import requests

app = Flask(__name__)

# Facebook Page Access Token aur Verify Token
PAGE_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

# Function to send message
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=data)

# Webhook for verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403

# Handling messages
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry"):
            messaging = entry.get("messaging", [])
            for event in messaging:
                if event.get("message"):
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]
                    send_message(sender_id, f"Bot: Aapne kaha '{message_text}'")
    return "Message Processed", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
