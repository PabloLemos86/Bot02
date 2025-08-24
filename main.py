# main.py
import os
import asyncio
from flask import Flask, request
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from datetime import datetime, timedelta

from config import TOKEN, REGIOES, DEFAULT_QTD
from utils.licitacoes import coletar_licitacoes, enviar_licitacoes

# ================================================
# FLASK APP PARA RENDER + UPTIMEROBOT
# ================================================
app = Flask(__name__)

# Configura o objeto Application para ser acessível globalmente
application = ApplicationBuilder().token(TOKEN).build()

# ================================================
# FUNÇÃO PARA CONFIGURAR O BOT
# ================================================
def setup_handlers():
    """Configura todos os handlers do bot."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pesquisar", comando_pesquisar))
    application.add_handler(CommandHandler("creditos", comando_creditos))
    application.add_handler(CommandHandler("agendar", comando_agendar))
    application.add_handler(CallbackQueryHandler(button_handler))

async def configurar_menu():
    """Configura o menu de comandos do bot."""
    comandos = [
        BotCommand("pesquisar", "🔍 Pesquisar licitações"),
        BotCommand("agendar", "📅 Agendar busca automática"),
        BotCommand("creditos", "💳 CRÉDITOS"),
    ]
    await application.bot.set_my_commands(comandos)
    print("✅ Menu de comandos do bot configurado com sucesso.")

# ================================================
# ENDPOINTS DO FLASK
# ================================================
@app.route("/")
def home():
    return "🤖 Bot está rodando no Render!"

@app.route(f"/{TOKEN}", methods=["POST"])
async def telegram_webhook():
    """Endpoint para receber atualizações do Telegram via POST."""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "ok"
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return "error", 500

# ================================================
# FUNÇÃO PARA RODAR O SERVIDOR
# ================================================
async def main():
    """Função principal para iniciar o servidor Flask e o bot."""
    print("Iniciando o bot...")
    setup_handlers()
    await configurar_menu()

    # Define o webhook no Telegram
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL")
    if webhook_url:
        full_webhook_url = f"{webhook_url}/{TOKEN}"
        await application.bot.set_webhook(url=full_webhook_url)
        print(f"✅ Webhook definido para: {full_webhook_url}")

    # Inicia o servidor Flask
    port = int(os.environ.get("PORT", 5000))
    # Flask não é assíncrono, então ele precisa ser rodado em um loop de evento separado
    from gunicorn.app.wsgiapp import WSGIApplication
    
    # Para o Render, Gunicorn é uma boa escolha.
    # Você pode rodar gunicorn via Procfile:
    # `web: gunicorn --bind 0.0.0.0:$PORT main:app --worker-class gevent`

    print("🚫 Você precisa configurar o seu 'Procfile' para usar o Gunicorn.")
    print("🌐 O servidor Flask deve ser iniciado com 'gunicorn main:app'")

# ================================================
# COMANDOS DO BOT (mantidos)
# ================================================
# ... (os comandos e handlers do seu bot continuam aqui, sem alterações)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bem-vindo! Use o botão ☰ Menu abaixo para começar.")

async def comando_pesquisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌎 Norte", callback_data="regiao_Norte")],
        [InlineKeyboardButton("🌎 Nordeste", callback_data="regiao_Nordeste")],
        [InlineKeyboardButton("🌎 Centro-Oeste", callback_data="regiao_Centro-Oeste")],
        [InlineKeyboardButton("🌎 Sudeste", callback_data="regiao_Sudeste")],
        [InlineKeyboardButton("🌎 Sul", callback_data="regiao_Sul")],
        [InlineKeyboardButton("🌎 Nacional", callback_data="regiao_Nacional")],
    ]
    await update.message.reply_text("Selecione a região:", reply_markup=InlineKeyboardMarkup(keyboard))

async def comando_creditos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("20 créditos – R$0,01", callback_data="recarga_20")],
        [InlineKeyboardButton("50 créditos – R$0,02", callback_data="recarga_50")],
        [InlineKeyboardButton("80 créditos – R$0,03", callback_data="recarga_80")],
    ]
    await update.message.reply_text(
        "💳 Seu saldo atual é: 10 créditos.\n\nEscolha uma opção para recarregar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def comando_agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Em breve você poderá agendar pesquisas automáticas!")

# ================================================
# HANDLER DE BOTÕES (mantido)
# ================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("regiao_"):
        regiao = data.split("_")[1]
        context.user_data["regiao"] = regiao
        estados = REGIOES.get(regiao, [])
        if estados:
            keyboard = [[InlineKeyboardButton(uf, callback_data=f"estado_{uf}") for uf in estados[i:i+3]] for i in range(0, len(estados), 3)]
            await query.edit_message_text(
                f"Região *{regiao}* selecionada. Agora escolha o estado:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            context.user_data["uf"] = None
            await mostrar_opcoes_periodo(query)
        return

    if data.startswith("estado_"):
        uf = data.split("_")[1]
        context.user_data["uf"] = uf
        await mostrar_opcoes_periodo(query)
        return

    if data.startswith("periodo_"):
        dias = int(data.split("_")[1])
        hoje = datetime.now()
        data_inicial = hoje - timedelta(days=dias)
        data_final = hoje
        uf = context.user_data.get("uf")
        await query.edit_message_text(
            f"🔍 Buscando licitações para `{uf or 'Brasil inteiro'}` de {data_inicial.date()} a {data_final.date()}...",
            parse_mode="Markdown"
        )
        lics = coletar_licitacoes(data_inicial.strftime("%Y%m%d"), data_final.strftime("%Y%m%d"), uf=uf, limite=DEFAULT_QTD)
        if not lics:
            await query.message.reply_text("⚠️ Nenhuma licitação encontrada.")
            return
        await enviar_licitacoes(query, lics)
        return

    if data.startswith("recarga_"):
        valor = data.split("_")[1]
        creditos_map = {"20": "R$0,01", "50": "R$0,02", "80": "R$0,03"}
        valor_real = creditos_map.get(valor, "valor desconhecido")
        await query.edit_message_text(
            f"✅ Você escolheu recarregar {valor} créditos por {valor_real}.\n\n🔜 Em breve o pagamento será processado!"
        )

# ================================================
# OPÇÕES DE PERÍODO (mantido)
# ================================================
async def mostrar_opcoes_periodo(query):
    keyboard = [
        [InlineKeyboardButton("🗓️ Últimos 7 dias", callback_data="periodo_7")],
        [InlineKeyboardButton("🗓️ Últimos 15 dias", callback_data="periodo_15")],
        [InlineKeyboardButton("🗓️ 1 mês", callback_data="periodo_30")],
        [InlineKeyboardButton("🗓️ 3 meses", callback_data="periodo_90")],
    ]
    await query.edit_message_text("Agora selecione o período:", reply_markup=InlineKeyboardMarkup(keyboard))
    
# ================================================
# MAIN DO SCRIPT
# ================================================
if __name__ == "__main__":
    # Inicia o loop de evento para executar a configuração assíncrona
    try:
        asyncio.run(main())
    except RuntimeError:
        pass  # Ocorre se o loop já estiver rodando (no caso do Gunicorn)
    
    # Inicia o servidor Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
