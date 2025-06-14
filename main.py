from flask import Flask, request
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (new syntax)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    return 'I am live, Joy v0.3!'

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403

    if request.method == "POST":
        data = request.get_json()
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {}).get("text")
                if sender_id and message:
                    reply = generate_ai_reply(message)
                    send_fb_message(sender_id, reply)

            for change in entry.get("changes", []):
                if change.get("field") == "feed":
                    value = change.get("value", {})
                    if value.get("item") == "comment" and value.get("verb") == "add":
                        comment_id = value.get("comment_id")
                        comment_message = value.get("message")
                        if comment_id and comment_message:
                            reply = generate_ai_reply(comment_message)
                            reply_to_comment(comment_id, reply)
        return "OK", 200

def generate_ai_reply(message_text):
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "You are a friendly customer support girl assistant for an online shop. So you don't need to answer in very long text, just finish your reply as short as possible. You are multilingual, so reply in the customer's language."},
                {"role": "user", "content": message_text}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, something went wrong v0.3."

def send_fb_message(recipient_id, message_text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.post(url, json=payload)
    print("Messenger response:", response.status_code, response.text)

def reply_to_comment(comment_id, message_text):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    data = {
        "message": message_text
    }
    response = requests.post(url, params=params, data=data)
    print("Comment reply response:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
