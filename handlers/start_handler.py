# handlers/start_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "I am Atlaslive Sportsbook bot. Let's explore my functions:"
    )

    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("Create Bet", callback_data='create_bet')],
        [InlineKeyboardButton("View Bets", callback_data='view_bets')],
        [InlineKeyboardButton("Accept Bet", callback_data='accept_bet')],
        [InlineKeyboardButton("Calculate Result", callback_data='calculate_result')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
