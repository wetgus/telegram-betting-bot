# handlers/accept_bet_handler.py

from telegram import Update
from telegram.ext import ContextTypes

bets = {}  # Make sure to import the bets dictionary or use a shared state

async def accept_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /accept_bet <bet_id> <your_bet>")
        return
    
    bet_id = int(context.args[0])
    user_bet = context.args[1]
    
    if bet_id not in bets:
        await update.message.reply_text("Bet ID does not exist.")
        return
    
    bets[bet_id]['user_bets'][update.effective_user.username] = user_bet
    await update.message.reply_text(f"You have accepted the bet {bet_id} with your prediction: {user_bet}")

