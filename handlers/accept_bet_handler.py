from telegram import Update
from telegram.ext import ContextTypes

async def accept_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to accept a bet."""
    await update.callback_query.answer()  # Acknowledge the callback
    await update.callback_query.message.reply_text("Please provide the bet ID you want to accept and your prediction.")
