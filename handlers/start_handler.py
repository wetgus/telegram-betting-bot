# handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from handlers.welcome_message import WELCOME_MESSAGE  # Import the welcome message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)  # Use the imported welcome message
