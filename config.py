# config.py
import os

# Token do Bot (do BotFather)
TOKEN = os.getenv("TOKEN")

# URL pública do Render (ex: https://seubot.onrender.com)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Se for "1", roda em modo webhook (Render); caso contrário, polling (local)
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "0")

# Porta (Render define automaticamente)
PORT = int(os.getenv("PORT", 5000))