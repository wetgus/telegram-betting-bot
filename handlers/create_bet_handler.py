import logging
from datetime import datetime
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE, PREDEFINED_COLLECTION

# Set up logging
logger = logging.getLogger(__name__)

# States for the conversation
MATCH_SELECTION, OUTCOME_SELECTION, BET_AMOUNT = range(3)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]
markets_collection = db[PREDEFINED_COLLECTION]

async def start(update: Update, context: CallbackContext) -> int:
    logger.debug("Starting bet creation process.")
    
    # Fetch matches from the database
    try:
        markets = markets_collection.find({})
        match_buttons = []

        for market in markets:
            for match in market.get('matches', []):
                button = InlineKeyboardButton(
                    text=match['name'],
                    callback_data=f"match:{match['name']}"
                )
                match_buttons.append([button])
        
        if not match_buttons:
            await update.message.reply_text("No matches available.")
            return ConversationHandler.END
        
        logger.debug("Matches fetched successfully. Sending buttons.")
        await update.message.reply_text("Please select a match:", reply_markup=InlineKeyboardMarkup(match_buttons))
        return MATCH_SELECTION
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        await update.message.reply_text("Error fetching matches. Please try again later.")
        return ConversationHandler.END

async def select_outcome(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    match_name = query.data.split(':')[1]  # Extract the match name from callback data
    logger.debug(f"Match selected: {match_name}")

    # Fetch outcomes for the selected match
    try:
        market = markets_collection.find_one({"matches.name": match_name})
        if market:
            for match in market.get('matches', []):
                if match['name'] == match_name:
                    outcome_buttons = [
                        InlineKeyboardButton(outcome, callback_data=f"outcome:{outcome}") 
                        for outcome in match['outcomes']
                    ]
                    await query.message.reply_text("Please select an outcome:", 
                                                    reply_markup=InlineKeyboardMarkup([outcome_buttons]))
                    return OUTCOME_SELECTION

        await query.message.reply_text("No outcomes found for this match.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error fetching outcomes: {e}")
        await query.message.reply_text("Error fetching outcomes. Please try again later.")
        return ConversationHandler.END

async def enter_bet_amount(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    outcome = query.data.split(':')[1]  # Extract the outcome from callback data
    logger.debug(f"Outcome selected: {outcome}")

    # Store selected outcome in user data
    context.user_data['selected_outcome'] = outcome
    await query.message.reply_text("Enter the amount (1 to 100):")
    
    return BET_AMOUNT

async def finalize_bet(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    try:
        amount = int(amount)
        if 1 <= amount <= 100:
            bet_data = {
                "bet_description": context.user_data['selected_outcome'],
                "amount": amount,
                "user_id": update.message.from_user.id,
                "creation_date": datetime.now().isoformat()
            }
            result = bets_collection.insert_one(bet_data)
            logger.info(f"Bet successfully saved to MongoDB: {bet_data}")
            await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Invalid amount. Please enter an integer between 1 and 100.")
            return BET_AMOUNT
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter an integer between 1 and 100.")
        return BET_AMOUNT

create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        MATCH_SELECTION: [CallbackQueryHandler(select_outcome)],
        OUTCOME_SELECTION: [CallbackQueryHandler(enter_bet_amount)],
        BET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalize_bet)],
    },
    fallbacks=[],
)
