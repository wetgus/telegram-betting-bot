from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

# Menu items
menu_keyboard = [['Create Bet', 'View Bets'], ['Help', 'Cancel']]

def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Welcome to the Betting Bot! Please choose an option:",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("This bot allows you to create and manage bets. Use the menu to navigate.")

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Operation cancelled.")
