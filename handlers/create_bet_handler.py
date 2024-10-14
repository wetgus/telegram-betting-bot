import logging
from pymongo import MongoClient
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb+srv://wetgusbetting:TkfsEmL75Ue9aa8V@cluster0.3gl5y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["BetsBot"]  # Replace with your database name
bets_collection = db["Bets"]

# Define the states
BET_TYPE, AMOUNT = range(2)

# Function to handle entering the bet type
async def enter_bet_type(update: Update, context: CallbackContext) -> int:
    logger.info("Entering bet type...")
    await update.message.reply_text("Please enter the type of bet:")
    return BET_TYPE

# Function to handle entering the amount
async def enter_amount(update: Update, context: CallbackContext) -> int:
    logger.info("Bet type received: %s", update.message.text)
    context.user_data['bet_type'] = update.message.text
    await update.message.reply_text("Please enter the amount:")
    return AMOUNT

# Function to write bet to MongoDB
async def write_bet_to_mongo(bet):
    try:
        bets_collection.insert_one(bet)
        logger.info("Bet successfully saved to MongoDB: %s", bet)
    except Exception as e:
        logger.error("Failed to save bet to MongoDB: %s", e)

# Function to handle the completion of the bet creation
async def create_bet(update: Update, context: CallbackContext) -> int:
    bet = {
        'bet_type': context.user_data['bet_type'],
        'amount': update.message.text,
        'user_id': update.message.from_user.id
    }
    logger.info("Creating bet with data: %s", bet)
    await write_bet_to_mongo(bet)
    await update.message.reply_text("Your bet has been created!")
    return ConversationHandler.END

# Define the conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', enter_bet_type)],
    states={
        BET_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_bet)],
    },
    fallbacks=[],
)
