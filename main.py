# main.py
import os
from flask import Flask, request
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    Updater
)
from datetime import datetime, timedelta

from config import TOKEN, REGIOES, DEFAULT_QTD
from utils.licitacoes import coletar_licitacoes, enviar_licitacoes

# ================================================
# FLASK APP PARA RENDER + UPTIMEROBOT
# ================================================
app = Flask(__name__)

# ================================================
# FUNÇÃO PARA RODAR O BOT (AGORA COM WEBHOOK)
# ================================================
def setup_bot():
    """Configura o bot com a API do Telegram e o webhook."""
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pesquisar", comando_pesquisar))
    application.add_handler(CommandHandler("creditos", comando_creditos))
    application.add_handler(CommandHandler("agendar", comando_agendar))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.post_init = configurar_menu
    return application

async def set_webhook(app_bot):
    """Define a URL do webhook no Telegram."""
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL")
    if webhook_url:
        print(f"Setting webhook URL to {webhook_url}")
        await app_bot.bot.set_webhook(url=webhook_url)

# ================================================
# ENDPOINTS DO FLASK
# ================================================
application = setup_bot()

@app.route("/")
def home():
    return "🤖 Bot está rodando no Render!"

@app.route("/telegram", methods=["POST"])
async def telegram_webhook():
    """Endpoint para receber atualizações do Telegram."""
    await application.process_update(
        Update.de_json(request.get_json(force=True), application.bot)
    )
    return "ok"

# ================================================
# COMANDOS DO BOT (MANTIDOS)
# ================================================
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
# HANDLER DE BOTÕES (MANTIDO)
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
# OPÇÕES DE PERÍODO (MANTIDO)
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
# CONFIGURAÇÃO DO MENU (MANTIDO)
# ================================================
async def configurar_menu(app):
    comandos = [
        BotCommand("pesquisar", "🔍 Pesquisar licitações"),
        BotCommand("agendar", "📅 Agendar busca automática"),
        BotCommand("creditos", "💳 CRÉDITOS"),
    ]
    await app.bot.set_my_commands(comandos)
    
# ================================================
# MAIN
# ================================================
if __name__ == "__main__":
    # Inicia Flask para Render e configura o webhook
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
