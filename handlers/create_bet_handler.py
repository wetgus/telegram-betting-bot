# create_bet_handler.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from pymongo import MongoClient
from config import MONGODB_URI

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client['your_database_name']  # Replace with your database name
bets_collection = db['bets']  # Replace with your collection name

# States
AWAITING_DESCRIPTION, AWAITING_AMOUNT = range(2)

# Logger setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please enter the bet description (1 to 200 characters):")
    return AWAITING_DESCRIPTION

async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description = update.message.text.strip()

    if len(description) < 1 or len(description) > 200:
        await update.message.reply_text("Invalid input. Please enter the bet description (1 to 200 characters):")
        return AWAITING_DESCRIPTION

    context.user_data['bet'] = {'description': description}
    await update.message.reply_text("Please enter the bet amount (1 to 100):")
    return AWAITING_AMOUNT

async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    amount_text = update.message.text.strip()

    try:
        amount = int(amount_text)
        if amount < 1 or amount > 100:
            raise ValueError("Amount must be between 1 and 100.")
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter the bet amount (1 to 100):")
        return AWAITING_AMOUNT

    bet = context.user_data['bet']
    bet['amount'] = amount
    await write_bet_to_mongodb(bet)
    await update.message.reply_text(f'Bet "{bet["description"]}" is accepted with {bet["amount"]} on stake.')
    return ConversationHandler.END

async def write_bet_to_mongodb(bet):
    bets_collection.insert_one(bet)

def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update.message.reply_text('Bet creation cancelled.')
    return ConversationHandler.END

# Define the conversation handler
create_bet_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        AWAITING_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, enter_description)],
        AWAITING_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, enter_amount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
