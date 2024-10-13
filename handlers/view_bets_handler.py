# handlers/view_bets_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID

bets = {}  # Make sure to import the bets dictionary or use a shared state

async def view_bets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You do not have permission to view the bets.")
        return

    if not bets:
        await update.message.reply_text("No bets have been created yet.")
        return
    
    response = "Current Bets:\n"
    for bet_id, bet_info in bets.items():
        response += f"Bet ID: {bet_id}\nDescription: {bet_info['description']}\nEnd Date: {bet_info['end_date']}\n"
        if bet_info['user_bets']:
            response += "Predictions:\n"
            for user, prediction in bet_info['user_bets'].items():
                response += f"- {user}: {prediction}\n"
        else:
            response += "No predictions yet.\n"
        response += "\n"

    await update.message.reply_text(response)

