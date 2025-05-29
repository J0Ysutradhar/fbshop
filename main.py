from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

# Replace with your actual values
VERIFY_TOKEN = 'fbshop'  # Can be any string
PAGE_ACCESS_TOKEN = 'EAAYjAWyeiBoBO80x3d7XZC1ISxqZCrIJ92ONGSWipdZAZBhdrdz3c2u2ZClsGhSqwT4ZB1OjUdyOZAV0N7WIxZBLNMHVSIy3WCxmw98ZCwvHJRDPzg5hAfzWaWXUB5oZBaZA1cUgYZB54tw7KkpEBgPqgvu8ZA7wwZBqRyoonkALjeKaXpUMLjyxmZA6ANZBuHCiySWpGN5TJSSDsZCeFqgZDZD'
OPENAI_API_KEY = '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'

openai.api_key = OPENAI_API_KEY

@app.route("/", methods=['GET'])
def home():
    return "Meta AI bot is running!"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # For verifying webhook with Facebook
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    if request.method == 'POST':
        output = request.get_json()
        for entry in output.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                if messaging_event.get('message') and 'text' in messaging_event['message']:
                    message_text = messaging_event['message']['text']
                    reply = generate_ai_reply(message_text)
                    send_fb_message(sender_id, reply)
        return "Message Processed", 200

def generate_ai_reply(user_message):
    prompt = f"You are a helpful assistant for a Facebook online shop. Reply nicely to: {user_message}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4 if you have access
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def send_fb_message(recipient_id, message):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
