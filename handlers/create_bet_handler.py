import logging
from datetime import datetime
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update, InlineKeyboardMarkup
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION, PREDEFINED_COLLECTION

# Set up logging
logger = logging.getLogger(__name__)

# States for the conversation
SELECT_MATCH, SELECT_OUTCOME, BET_AMOUNT = range(3)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

# Use aliases for collections
bets_collection = db[MONGODB_COLLECTION]  # Placed bets
markets_collection = db[PREDEFINED_COLLECTION]  # Selections

async def start(update: Update, context: CallbackContext) -> int:
    # Fetch matches from MongoDB
    markets = markets_collection.find()
    matches = []

    for market in markets:
        for match in market.get("matches", []):
            matches.append((match["name"], match["outcomes"]))

    if not matches:
        await update.message.reply_text("No matches available.")
        return ConversationHandler.END

    # Store matches in user_data for later use
    context.user_data['matches'] = matches

    # Prompt the user to select a match
    match_buttons = [[f"{match[0]}"] for match in matches]  # Format for buttons
    await update.message.reply_text("Please select a match:", reply_markup=InlineKeyboardMarkup(match_buttons))
    
    return SELECT_MATCH

async def select_match(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    selected_match = query.data
    context.user_data['selected_match'] = selected_match

    # Fetch outcomes for the selected match
    for market in context.user_data['matches']:
        if market[0] == selected_match:
            context.user_data['outcomes'] = market[1]  # Store outcomes for the selected match

    # Prompt the user to select an outcome
    outcome_buttons = [[f"{outcome}"] for outcome in context.user_data['outcomes']]
    await query.message.reply_text("Please select an outcome:", reply_markup=InlineKeyboardMarkup(outcome_buttons))
    
    return SELECT_OUTCOME

async def select_outcome(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    selected_outcome = query.data
    context.user_data['selected_outcome'] = selected_outcome

    # Prompt the user for the bet amount
    await query.message.reply_text("Enter the amount: (1 to 100)")
    
    return BET_AMOUNT

async def enter_bet_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    try:
        amount = int(amount)
        if 1 <= amount <= 100:
            bet_data = {
                "match": context.user_data['selected_match'],
                "outcome": context.user_data['selected_outcome'],
                "amount": amount,
                "user_id": update.message.from_user.id,
                "creation_date": datetime.now().isoformat()  # Add creation date
            }
            result = bets_collection.insert_one(bet_data)  # Use bets_collection to store bets
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
        SELECT_MATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_match)],
        SELECT_OUTCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_outcome)],
        BET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bet_amount)],
    },
    fallbacks=[],
)
