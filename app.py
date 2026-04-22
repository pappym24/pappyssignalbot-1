from flask import Flask, request, jsonify
import anthropic
import requests
import os

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    result = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })
    print(f"Telegram response: {result.status_code} - {result.text}")
    return result

@app.route("/webhook", methods=["POST"])
def webhook():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.get_json(force=True)
    
    alert_message = data.get("message", "")
    price = data.get("price", "N/A")
    sl = data.get("sl", "N/A")
    tp = data.get("tp", "N/A")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""You are a gold trading assistant.
A TradingView alert just fired for XAU/USD:
Alert: {alert_message}
Entry Price: {price}
Stop Loss: {sl}
Take Profit: {tp}

Confirm if this is a valid setup and give a 2-sentence analysis."""
        }]
    )

    analysis = response.content[0].text
    final_message = f"""🚨 *XAU/USD SIGNAL*
📈 Entry: {price}
🛑 SL: {sl}
✅ TP: {tp}
📊 Signal: {alert_message}

🤖 *Claude:*
{analysis}"""

    send_telegram(final_message)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
