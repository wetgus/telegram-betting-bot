# handlers/create_bet_handler.py

from telegram import Update
from telegram.ext import ContextTypes

bets = {}  # Initialize a global variable to hold bets

async def create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /create_bet <bet_description> <end_date>")
        return
    
    bet_description = context.args[0]
    end_date = context.args[1]  # You can add date validation later
    bet_id = len(bets) + 1  # Simple ID assignment
    
    bets[bet_id] = {
        'description': bet_description,
        'end_date': end_date,
        'user_bets': {}
    }
    
    await update.message.reply_text(f"Bet created with ID: {bet_id}")
