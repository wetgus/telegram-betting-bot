import json
from datetime import datetime
import random
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

# Constants for conversation stages
BET_DESCRIPTION, BET_AMOUNT = range(2)

# Dummy database file (JSON)
DATABASE_FILE = 'bets.json'

def load_bets():
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bet(bet_data):
    bets = load_bets()
    bets[bet_data['id']] = bet_data
    with open(DATABASE_FILE, 'w') as f:
        json.dump(bets, f, indent=4)

def create_bet(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter the description of the bet:")
    return BET_DESCRIPTION

def bet_description(update: Update, context: CallbackContext):
    context.user_data['description'] = update.message.text
    update.message.reply_text("Great! Now enter the bet amount:")
    return BET_AMOUNT

def bet_amount(update: Update, context: CallbackContext):
    try:
        amount = float(update.message.text)
    except ValueError:
        update.message.reply_text("Please enter a valid amount.")
        return BET_AMOUNT

    description = context.user_data['description']
    user_id = update.message.from_user.id
    bet_id = random.randint(100000, 999999)
    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    bet_data = {
        'id': bet_id,
        'user_id': user_id,
        'description': description,
        'amount': amount,
        'date_created': date_created
    }
    
    save_bet(bet_data)
    update.message.reply_text(f"Bet created successfully! Your bet ID is: {bet_id}")

    return ConversationHandler.END

def view_bets(update: Update, context: CallbackContext):
    bets = load_bets()
    if bets:
        message = "Here are your bets:\n"
        for bet_id, bet in bets.items():
            message += f"\nID: {bet_id}, Description: {bet['description']}, Amount: {bet['amount']}, Date: {bet['date_created']}"
    else:
        message = "You have no bets yet."
    update.message.reply_text(message)
