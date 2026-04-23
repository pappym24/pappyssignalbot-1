from flask import Flask, request, jsonify
import anthropic
import requests
import os

app = Flask(__name__)

def send_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    result = requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })
    print(f"Telegram response: {result.status_code} - {result.text}")
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        import json
        raw = request.get_data(as_text=True)
        print(f"Raw request: {raw}")
        data = json.loads(raw)

        alert_message = data.get("message", "no message")
        price = data.get("price", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")

      api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key, timeout=25.0)
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=150,
    messages=[{
        "role": "user",
        "content": f"Gold trade alert: {alert_message} at price {price}, SL {sl}, TP {tp}. Give a 1 sentence verdict: BUY or SELL and why."
    }]
)
Give a 2 sentence analysis and confirm if valid."""
            }]
        )

        analysis = response.content[0].text
        final_message = f"XAU/USD SIGNAL\nEntry: {price}\nSL: {sl}\nTP: {tp}\nSignal: {alert_message}\n\nClaude: {analysis}"
        send_telegram(final_message)
        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 200
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
