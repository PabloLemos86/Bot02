# main.py (modo webhook para Render)

import threading
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder

import config
import handlers  # importando o módulo inteiro para evitar conflito de nomes

# ---------- validações ----------
if not config.TOKEN or len(config.TOKEN.strip()) < 30:
    raise RuntimeError("TOKEN ausente ou inválido. Configure no Render em Environment Variables.")

if config.USE_WEBHOOK != "1":
    raise RuntimeError("Esse main.py deve ser usado apenas em modo WEBHOOK (Render).")

# ---------- instancia o bot ----------
application = ApplicationBuilder().token(config.TOKEN.strip()).build()
handlers.registrar_handlers(application)  # registra handlers do módulo

# ---------- Flask ----------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "🤖 Bot ativo (WEBHOOK).", 200

@app_flask.route(f"/{config.TOKEN}", methods=["POST"])
def telegram_webhook():
    """Endpoint chamado pelo Telegram (modo webhook)."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# ---------- ciclo webhook ----------
def _run_webhook_lifecycle():
    async def _main():
        await application.initialize()
        await application.start()

        if not config.WEBHOOK_URL:
            raise RuntimeError("WEBHOOK_URL não definido no ambiente (Render).")

        url = f"{config.WEBHOOK_URL.rstrip('/')}/{config.TOKEN}"
        await application.bot.set_webhook(url)
        print(f"[BOOT] Webhook registrado em: {url}")

        # Mantém o loop ativo
        await asyncio.Event().wait()

    asyncio.run(_main())

# ---------- execução ----------
if __name__ == "__main__":
    print(f"[BOOT] Iniciando bot em modo WEBHOOK | URL={config.WEBHOOK_URL}")

    # Thread para rodar o loop do bot
    threading.Thread(target=_run_webhook_lifecycle, daemon=True).start()

    # Flask fica na thread principal
    app_flask.run(host="0.0.0.0", port=config.PORT)