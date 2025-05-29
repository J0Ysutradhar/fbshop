from flask import Flask, request
import requests
import os
from openai import OpenAI




app = Flask(__name__)
VERIFY_TOKEN = 'fbshop'
PAGE_ACCESS_TOKEN = 'EAAYjAWyeiBoBO80x3d7XZC1ISxqZCrIJ92ONGSWipdZAZBhdrdz3c2u2ZClsGhSqwT4ZB1OjUdyOZAV0N7WIxZBLNMHVSIy3WCxmw98ZCwvHJRDPzg5hAfzWaWXUB5oZBaZA1cUgYZB54tw7KkpEBgPqgvu8ZA7wwZBqRyoonkALjeKaXpUMLjyxmZA6ANZBuHCiySWpGN5TJSSDsZCeFqgZDZD'
OPENAI_API_KEY = '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'
# Initialize OpenAI client (new syntax)
client = OpenAI(api_key=OPENAI_API_KEY)
@app.route('/')
def home():
    return 'Joy Im live'
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403

    if request.method == "POST":
        data = request.get_json()
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                message = messaging_event.get("message", {}).get("text")
                if sender_id and message:
                    reply = generate_ai_reply(message)
                    send_fb_message(sender_id, reply)
        return "OK", 200

def generate_ai_reply(message_text):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly customer support assistant for an online shop."},
                {"role": "user", "content": message_text}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, something went wrong."

def send_fb_message(recipient_id, message_text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.post(url, json=payload)
    print("Facebook response:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
