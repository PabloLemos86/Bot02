# main.py
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from config import TOKEN, WEBHOOK_URL
from handlers import (
    start,
    comando_pesquisar,
    comando_creditos,
    comando_agendar,
    button_handler,
    configurar_menu,
)

# Flask app
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "🤖 Bot está rodando no Render!"

# Inicializa o bot
application = ApplicationBuilder().token(TOKEN).build()

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("pesquisar", comando_pesquisar))
application.add_handler(CommandHandler("creditos", comando_creditos))
application.add_handler(CommandHandler("agendar", comando_agendar))
application.add_handler(CallbackQueryHandler(button_handler))
application.post_init = configurar_menu

# Webhook endpoint
@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

# Define o webhook ao iniciar
@app_flask.before_first_request
def set_webhook():
    application.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)