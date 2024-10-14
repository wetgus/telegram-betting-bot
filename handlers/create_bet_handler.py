import logging
from datetime import datetime
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION

# Set up logging
logger = logging.getLogger(__name__)

# States for the conversation
BET_DESCRIPTION, BET_AMOUNT = range(2)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]
bets_collection = db[MONGODB_COLLECTION]

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Enter bet description (1 to 200 symbols):")
    return BET_DESCRIPTION

async def enter_bet_description(update: Update, context: CallbackContext) -> int:
    description = update.message.text
    if 1 <= len(description) <= 200:
        context.user_data['bet_description'] = description
        await update.message.reply_text("Enter the amount: (1 to 100)")
        return BET_AMOUNT
    else:
        await update.message.reply_text("Invalid input. Please enter a description between 1 to 200 symbols:")
        return BET_DESCRIPTION

async def enter_bet_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    try:
        amount = int(amount)
        if 1 <= amount <= 100:
            bet_data = {
                "bet_description": context.user_data['bet_description'],
                "amount": amount,
                "user_id": update.message.from_user.id,
                "creation_date": datetime.now().isoformat()  # Add creation date
            }
            result = bets_collection.insert_one(bet_data)
            logger.info(f"Bet successfully saved to MongoDB: {bet_data}")
            await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Invalid amount. Please enter an integer between 1 and 100:")
            return BET_AMOUNT
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter an integer between 1 and 100:")
        return BET_AMOUNT

create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        BET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bet_description)],
        BET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bet_amount)],
    },
    fallbacks=[],
)
