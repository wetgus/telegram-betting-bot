import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (ConversationHandler, CommandHandler, MessageHandler,
                            filters, ContextTypes)
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION, PREDEFINED_COLLECTION

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
SELECT_SPORT, SELECT_MATCH, SELECT_OUTCOME, ENTER_AMOUNT = range(4)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("You clicked Create Bet! Please select a sport:")
    return await select_sport(update, context)

async def select_sport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    collection = db[PREDEFINED_COLLECTION]  # Access the predefined collection
    sports_documents = await collection.find({}).to_list(None)  # Retrieve all documents
    sports = [doc['sport_name'] for doc in sports_documents]  # Adjust according to your document structure
    
    if not sports:
        await update.message.reply_text("No sports available.")
        return ConversationHandler.END

    sports_message = "Please select a sport:\n" + "\n".join([f"/{sport}" for sport in sports])
    
    await update.message.reply_text(sports_message)
    return SELECT_MATCH  # Move to the next state

async def select_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Here you can implement similar logic for selecting matches based on the chosen sport.
    selected_sport = update.message.text.strip()[1:]  # Remove leading slash
    await update.message.reply_text(f"You selected {selected_sport}. Now please select a match.")
    # Logic for selecting a match goes here
    return SELECT_OUTCOME

async def select_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Implement logic to select an outcome based on the selected match.
    selected_match = update.message.text.strip()  # This should come from the previous state
    await update.message.reply_text(f"You selected {selected_match}. Now please select an outcome.")
    # Logic for selecting an outcome goes here
    return ENTER_AMOUNT

async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter the amount: (1 to 100)")
    return ENTER_AMOUNT  # Wait for user input

async def save_bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    amount = int(update.message.text)
    creation_date = datetime.now()

    bet_data = {
        'user_id': user_id,
        'amount': amount,
        'creation_date': creation_date,
        # Include sport, match, and outcome here after selection
    }

    collection = db[MONGODB_COLLECTION]
    result = await collection.insert_one(bet_data)

    await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
    return ConversationHandler.END

def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def create_bet_conv_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('create_bet', start)],
        states={
            SELECT_SPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_sport)],
            SELECT_MATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_match)],
            SELECT_OUTCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_outcome)],
            ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_bet)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
