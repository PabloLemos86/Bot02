from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou seu bot no Render 🚀")

# /creditos
async def comando_creditos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Desenvolvido por Pablo ✨")

# /pesquisar
async def comando_pesquisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Em breve: função de pesquisa.")

# /agendar
async def comando_agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Confirmar", callback_data="ok")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Deseja confirmar o agendamento?", reply_markup=reply_markup)

# Handler de botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Você escolheu: {query.data}")

# Configura todos os handlers
def configurar_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("creditos", comando_creditos))
    application.add_handler(CommandHandler("pesquisar", comando_pesquisar))
    application.add_handler(CommandHandler("agendar", comando_agendar))
    application.add_handler(CallbackQueryHandler(button_handler))