from flask import Flask, request, jsonify
import anthropic
import requests
import os
import json
import threading

app = Flask(__name__)

def process_alert(data):
    try:
        alert_message = data.get("message", "no message")
        price = data.get("price", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"XAU/USD alert: {alert_message} price {price} SL {sl} TP {tp}. One sentence: valid trade?"
            }]
        )

        analysis = response.content[0].text
        final_message = f"XAU/USD SIGNAL\nEntry: {price}\nSL: {sl}\nTP: {tp}\nSignal: {alert_message}\n\nClaude: {analysis}"
        
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        result = requests.post(url, data={
            "chat_id": chat_id,
            "text": final_message
        })
        print(f"Telegram: {result.status_code} - {result.text}")

    except Exception as e:
        print(f"Error in background: {str(e)}")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw = request.get_data(as_text=True)
        print(f"Raw: {raw}")
        data = json.loads(raw)
        
        # Respond immediately to TradingView
        thread = threading.Thread(target=process_alert, args=(data,))
        thread.start()
        
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
