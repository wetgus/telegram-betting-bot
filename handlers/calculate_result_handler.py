from telegram import Update
from telegram.ext import ContextTypes

async def calculate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to calculate the result of a bet."""
    await update.callback_query.answer()  # Acknowledge the callback
    await update.callback_query.message.reply_text("Please provide the bet ID and the actual result (yes/no).")
