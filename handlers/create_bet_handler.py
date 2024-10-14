from pymongo import MongoClient
from telegram import Update
from telegram.ext import (ConversationHandler, CommandHandler, MessageHandler,
                            filters, CallbackContext)
from config import MONGODB_URI

# MongoDB client setup
client = MongoClient(MONGODB_URI)
db = client['BetsBot']  # Replace with your actual database name
bets_collection = db['Bets']      # Replace with your actual collection name

# Define conversation states
BET_TYPE, AMOUNT = range(2)

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please choose a bet type: (e.g., win, place)")
    return BET_TYPE

async def enter_bet_type(update: Update, context: CallbackContext) -> int:
    bet_type = update.message.text
    context.user_data['bet_type'] = bet_type  # Save bet type in user data
    await update.message.reply_text("Please enter the amount for your bet:")
    return AMOUNT

async def enter_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    bet_type = context.user_data.get('bet_type')

    # Save to MongoDB
    bet_data = {
        'bet_type': bet_type,
        'amount': amount,
    }
    
    # Insert the bet into the MongoDB collection
    bets_collection.insert_one(bet_data)

    await update.message.reply_text(f"Bet created: Type - {bet_type}, Amount - {amount}.")
    return ConversationHandler.END

# Define conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        BET_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bet_type)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
    },
    fallbacks=[],
)
