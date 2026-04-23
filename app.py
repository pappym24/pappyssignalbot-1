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
    if request.is_json:
        data = request.get_json()
    else:
        data = request.get_json(force=True)

    alert_message = data.get("message", "")
    price = data.get("price", "N/A")
    sl = data.get("sl", "N/A")
    tp = data.get("tp", "N/A")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""You are a gold trading assistant.
A TradingView alert fired for XAU/USD:
Alert: {alert_message}
Entry Price: {price}
Stop Loss: {sl}
Take Profit: {tp}
Give a 2 sentence analysis and confirm if valid."""
        }]
    )

    analysis = response.content[0].text
    message = f"XAU/USD SIGNAL\nEntry: {price}\nSL: {sl}\nTP: {tp}\nSignal: {alert_message}\n\nClaude: {analysis}"
    send_telegram(message)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
