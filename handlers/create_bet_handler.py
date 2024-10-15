import logging
from datetime import datetime
from telegram.ext import (ConversationHandler, CommandHandler, 
                            MessageHandler, filters, CallbackQueryHandler, ContextTypes)
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Fetch matches and outcomes from the Markets collection
    markets = markets_collection.find()  # Get all markets from the collection
    match_buttons = []

    for market in markets:
        for match in market.get('matches', []):
            match_name = match['name']
            # Create a button for each match
            match_buttons.append(
                [InlineKeyboardButton(match_name, callback_data=match_name)]  # Use match name as callback data
            )

    reply_markup = InlineKeyboardMarkup(match_buttons)

    await update.message.reply_text("Please select a match:", reply_markup=reply_markup)
    return MATCH_SELECTION  # Go to the next state

async def select_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    match_name = query.data
    await query.answer()

    # Find the selected match's outcomes
    market = markets_collection.find_one({"matches.name": match_name})
    if market:
        outcomes = next(match for match in market['matches'] if match['name'] == match_name)['outcomes']
        outcome_buttons = [[InlineKeyboardButton(outcome, callback_data=outcome) for outcome in outcomes]]
        reply_markup = InlineKeyboardMarkup(outcome_buttons)

        await query.message.reply_text("Please select an outcome:", reply_markup=reply_markup)
        return OUTCOME_SELECTION  # Go to the next state
    else:
        await query.message.reply_text("Match not found.")
        return ConversationHandler.END

async def enter_bet_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    outcome = query.data
    await query.answer()

    context.user_data['bet_outcome'] = outcome  # Save the selected outcome
    await query.message.reply_text("Enter the amount (1 to 100):")
    return BET_AMOUNT  # Go to the next state

async def finalize_bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    amount = update.message.text
    try:
        amount = int(amount)
        if 1 <= amount <= 100:
            bet_data = {
                "bet_description": f"{context.user_data['bet_outcome']}",  # Use the selected outcome as description
                "amount": amount,
                "user_id": update.message.from_user.id,
                "creation_date": datetime.now().isoformat()  # Add creation date
            }
            bets_collection = db['Bets']  # Use the Bets collection
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
        MATCH_SELECTION: [CallbackQueryHandler(select_outcome)],
        OUTCOME_SELECTION: [CallbackQueryHandler(enter_bet_amount)],
        BET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalize_bet)],
    },
    fallbacks=[],
)
