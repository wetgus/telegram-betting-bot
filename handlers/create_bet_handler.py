from telegram import Update
from telegram.ext import ContextTypes

# Global variable to hold bets
bets = []

async def create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to provide bet details."""
    await update.callback_query.answer()  # Acknowledge the callback
    await update.callback_query.message.reply_text("Please provide the bet details in the format:\n`Bet description, End date (YYYY-MM-DD), Your prediction (yes/no)`")
    return WAITING_FOR_BET_DETAILS  # This signifies waiting for user input

async def handle_bet_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the details provided for creating a bet."""
    user_input = update.message.text  # Get user input
    try:
        description, end_date, prediction = user_input.split(', ')
        bets.append({'description': description, 'end_date': end_date, 'prediction': prediction})
        await update.message.reply_text("Bet created successfully!")
    except Exception:
        await update.message.reply_text("Invalid format. Please try again.")
