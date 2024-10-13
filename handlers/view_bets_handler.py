from telegram import Update
from telegram.ext import ContextTypes

# Import the global bets variable
from handlers.create_bet_handler import bets

async def view_bets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all created bets."""
    if not bets:
        await update.callback_query.message.reply_text("No bets have been created yet.")
    else:
        bet_list = "\n".join([f"{i + 1}. {bet['description']} - End Date: {bet['end_date']} - Prediction: {bet['prediction']}" for i, bet in enumerate(bets)])
        await update.callback_query.message.reply_text(f"Current Bets:\n{bet_list}")
