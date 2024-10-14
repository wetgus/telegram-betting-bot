import logging
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION

# Initialize MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client[MONGODB_DATABASE]
bets_collection = db[MONGODB_COLLECTION]

# Define states for the conversation
BET_TYPE, AMOUNT = range(2)

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /create_bet to start.")

# Create bet conversation entry point
async def enter_bet_type(update: Update, context: CallbackContext):
    await update.message.reply_text("Enter the bet type:")
    return BET_TYPE

async def receive_bet_type(update: Update, context: CallbackContext):
    bet_type = update.message.text
    context.user_data['bet_type'] = bet_type
    logging.info("Entering bet type...")
    logging.info(f"Bet type received: {bet_type}")

    await update.message.reply_text("Enter the amount:")
    return AMOUNT

async def receive_amount(update: Update, context: CallbackContext):
    amount = update.message.text
    bet_type = context.user_data['bet_type']
    user_id = update.message.from_user.id

    bet = {
        'bet_type': bet_type,
        'amount': amount,
        'user_id': user_id
    }

    logging.info("Creating bet with data: %s", bet)

    # Save bet to MongoDB
    await save_bet_to_db(bet)
    
    await update.message.reply_text("Bet created successfully!")
    return ConversationHandler.END

async def save_bet_to_db(bet):
    try:
        result = bets_collection.insert_one(bet)
        logging.info(f"Bet successfully saved to MongoDB: {bet}")
    except Exception as e:
        logging.error(f"Failed to save bet to MongoDB: {e}")

# Define the conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', enter_bet_type)],
    states={
        BET_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_bet_type)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
    },
    fallbacks=[],
)
