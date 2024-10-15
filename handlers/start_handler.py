# handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "I am Atlaslive Sportsbook bot. Let's explore my functions:\n"
        "/create_bet - initiates bet creation\n"
        "/balance - displays your current balance\n"
        "/help - shows available commands\n"
    )

    await update.message.reply_text(welcome_message)  # Send the welcome message without inline keyboard
