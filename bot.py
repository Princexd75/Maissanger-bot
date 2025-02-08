from flask import Flask, request
import requests

# Flask App Setup
app = Flask(__name__)

# Facebook Page Access Token (Yaha apna token daalo)
PAGE_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

# Function to send a message
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# Webhook Verification (Facebook Webhook Setup ke liye)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed"

# Handle Incoming Messages
@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for message_event in entry["messaging"]:
                if "message" in message_event:
                    sender_id = message_event["sender"]["id"]
                    message_text = message_event["message"]["text"]
                    
                    # Auto-reply logic
                    reply_text = f"Hi! You said: {message_text}"
                    send_message(sender_id, reply_text)

    return "OK", 200

# Run Flask App
if __name__ == "__main__":
    app.run(port=5000, debug=True)
