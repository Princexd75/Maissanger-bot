from flask import Flask, request
import requests
import schedule
import time
import threading
import openai

app = Flask(__name__)

# Facebook Messenger Bot Token & Verify Token
FB_ACCESS_TOKEN = "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN"
VERIFY_TOKEN = "YOUR_CUSTOM_VERIFY_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# List of restricted words
BAD_WORDS = ["badword1", "badword2", "badword3"]

# Poll storage
polls = {}

# Function to send a message via Messenger API
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "access_token": FB_ACCESS_TOKEN
    }
    requests.post(url, json=payload)

# Function to get AI-generated response
def get_ai_response(message):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response["choices"][0]["message"]["content"]

# Function to check for restricted words
def check_bad_words(message):
    for word in BAD_WORDS:
        if word in message.lower():
            return True
    return False

# Function to start a poll
def start_poll(question, options):
    poll_id = len(polls) + 1
    polls[poll_id] = {"question": question, "options": {opt: 0 for opt in options}}
    return poll_id

# Function to send a reminder
def send_reminder():
    send_message("GROUP_ID_HERE", "🔔 Reminder: Group meeting at 8 PM tonight!")

# Flask Webhook Endpoint
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':  # Facebook Webhook Verification
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    if request.method == 'POST':  # Facebook Message Handling
        data = request.get_json()
        message_event = data['entry'][0]['messaging'][0]
        sender_id = message_event['sender']['id']
        message_text = message_event.get('message', {}).get('text', '')

        if not message_text:
            return "ok", 200

        # Check for restricted words
        if check_bad_words(message_text):
            send_message(sender_id, "⚠️ Please use appropriate language!")
            return "ok", 200

        # Handle custom commands
        if message_text.startswith("/"):
            command = message_text.split(" ")[0].lower()

            if command == "/help":
                send_message(sender_id, "Bot Commands: /rules, /joke, /poll, /reminder")
            elif command == "/rules":
                send_message(sender_id, "🔹 No spamming \n🔹 No offensive language \n🔹 Respect everyone")
            elif command == "/joke":
                joke = requests.get("https://official-joke-api.appspot.com/random_joke").json()
                send_message(sender_id, f"{joke['setup']} - {joke['punchline']}")
            elif command == "/poll":
                parts = message_text.split('"')
                if len(parts) >= 3:
                    question = parts[1]
                    options = parts[2].strip().split()
                    poll_id = start_poll(question, options)
                    send_message(sender_id, f"📊 Poll started: {question}\nOptions: {', '.join(options)}\nVote using: /pollvote {poll_id} OPTION_NAME")
                else:
                    send_message(sender_id, "❌ To create a poll: /poll \"Question\" OPTION1 OPTION2")
            elif command == "/reminder":
                schedule.every().day.at("20:00").do(send_reminder)
                send_message(sender_id, "✅ Reminder set!")

            return "ok", 200

        # AI-Powered Responses
        ai_reply = get_ai_response(message_text)
        send_message(sender_id, ai_reply)

    return "ok", 200

# Background scheduler function
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in background
threading.Thread(target=run_scheduler).start()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
