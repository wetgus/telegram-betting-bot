# handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "I am Atlaslive Sportsbook bot. Let's explore my functions:\n\n"
        "Available commands:\n"
        "/create_bet - Create a new bet\n"
        "/view_bets - View all bets (Admin only)\n"
        "/accept_bet - Accept a bet and make a prediction\n"
        "/calculate_result - Calculate the result of a bet\n"
    )
    await update.message.reply_text(welcome_message)

