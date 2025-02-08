from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load environment variables
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "YOUR_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "YOUR_VERIFY_TOKEN")

# Facebook Messenger API URL
FB_URL = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

# Bot Memory (To track group activity)
group_memory = {}

# Function to send messages
def send_message(recipient_id, text):
    headers = {"Content-Type": "application/json"}
    message_data = {"recipient": {"id": recipient_id}, "message": {"text": text}}

    response = requests.post(FB_URL, json=message_data, headers=headers)
    if response.status_code != 200:
        logging.error(f"Error sending message: {response.text}")

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403

# Handle messages from Messenger (Groups & Individual Chats)
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    logging.info(f"Received data: {data}")

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            for event in messaging:
                sender_id = event["sender"]["id"]
                recipient_id = event["recipient"]["id"]

                if event.get("message"):
                    message_text = event["message"].get("text", "")

                    # Check if it's a group message
                    is_group_chat = sender_id != recipient_id  

                    if is_group_chat:
                        process_group_message(sender_id, recipient_id, message_text)
                    else:
                        send_message(sender_id, f"🤖 You said: '{message_text}'")

    return "Message Processed", 200

# Handle group messages
def process_group_message(sender_id, group_id, message_text):
    response_text = ""

    # Track group messages
    if group_id not in group_memory:
        group_memory[group_id] = []

    group_memory[group_id].append({"sender": sender_id, "message": message_text})

    # Basic Commands
    if "!ping" in message_text.lower():
        response_text = "🏓 Pong! I'm active in this group."
    
    elif "!members" in message_text.lower():
        response_text = f"👥 This group has {len(group_memory[group_id])} messages recorded."
    
    elif "!clear" in message_text.lower():
        group_memory[group_id] = []
        response_text = "🗑️ Group chat data cleared."

    else:
        response_text = f"👀 I see a new message: '{message_text}'"

    send_message(group_id, response_text)

# Run Flask app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
