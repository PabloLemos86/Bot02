import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder
from handlers import configurar_handlers

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ex: https://bot03.onrender.com

# Inicializa bot
application = ApplicationBuilder().token(TOKEN).build()
configurar_handlers(application)

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ativo com webhook!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

if __name__ == "__main__":
    # Configura webhook no Telegram
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))