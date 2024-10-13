# handlers/create_bet_handler.py

from telegram import Update
from telegram.ext import ContextTypes

# Global variable to hold bets
bets = []

async def create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()  # Acknowledge the callback
    await update.callback_query.message.reply_text("Please provide the bet details in the format:\n`Bet description, End date (YYYY-MM-DD), Your prediction (yes/no)`")
    return "WAITING_FOR_BET_DETAILS"  # This will signify we are waiting for user input
