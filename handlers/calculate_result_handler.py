# handlers/calculate_result_handler.py

from telegram import Update
from telegram.ext import ContextTypes

bets = {}  # Make sure to import the bets dictionary or use a shared state

async def calculate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /calculate_result <bet_id> <actual_result>")
        return
    
    bet_id = int(context.args[0])
    actual_result = context.args[1]
    
    if bet_id not in bets:
        await update.message.reply_text("Bet ID does not exist.")
        return
    
    # Determine the outcome
    winners = []
    for user, prediction in bets[bet_id]['user_bets'].items():
        if prediction == actual_result:
            winners.append(user)

    if winners:
        await update.message.reply_text(f"The winners for bet {bet_id} are: {', '.join(winners)}")
    else:
        await update.message.reply_text(f"No winners for bet {bet_id}.")

