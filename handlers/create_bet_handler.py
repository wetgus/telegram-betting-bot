from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import bets_collection, predefined_collection
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Define conversation states
SELECT_SPORT, SELECT_MATCH, SELECT_OUTCOME, ENTER_AMOUNT = range(4)

# Function to start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("User started creating a bet")
    
    sports = predefined_collection.distinct("sport")
    
    if not sports:
        await update.message.reply_text("No sports available.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(sport, callback_data=sport)] for sport in sports]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please select a sport:", reply_markup=reply_markup)
    
    return SELECT_SPORT

# Function to select a sport
async def select_sport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected_sport = query.data
    context.user_data['sport'] = selected_sport

    matches = predefined_collection.distinct("match", {"sport": selected_sport})
    
    if not matches:
        await query.edit_message_text(f"No matches available for {selected_sport}. Please try again.")
        return SELECT_SPORT

    keyboard = [[InlineKeyboardButton(match, callback_data=match)] for match in matches]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(f"Sport selected: {selected_sport}\nPlease select a match:", reply_markup=reply_markup)
    
    return SELECT_MATCH

# Function to select a match
async def select_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected_match = query.data
    context.user_data['match'] = selected_match

    outcomes = predefined_collection.distinct("outcome", {"match": selected_match})
    
    if not outcomes:
        await query.edit_message_text(f"No outcomes available for {selected_match}. Please try again.")
        return SELECT_MATCH

    keyboard = [[InlineKeyboardButton(outcome, callback_data=outcome)] for outcome in outcomes]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(f"Match selected: {selected_match}\nPlease select an outcome:", reply_markup=reply_markup)
    
    return SELECT_OUTCOME

# Function to select an outcome
async def select_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected_outcome = query.data
    context.user_data['outcome'] = selected_outcome

    await query.edit_message_text(f"Outcome selected: {selected_outcome}\nPlease enter the amount (1 to 100):")
    
    return ENTER_AMOUNT

# Function to enter the bet amount
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    amount_text = update.message.text
    
    if not amount_text.isdigit():
        await update.message.reply_text("Invalid amount. Please enter a number between 1 and 100.")
        return ENTER_AMOUNT

    amount = int(amount_text)
    
    if amount < 1 or amount > 100:
        await update.message.reply_text("Amount out of range. Please enter a number between 1 and 100.")
        return ENTER_AMOUNT

    context.user_data['amount'] = amount

    # Create the bet and save it to MongoDB
    bet_data = {
        "sport": context.user_data['sport'],
        "match": context.user_data['match'],
        "outcome": context.user_data['outcome'],
        "amount": amount,
        "user_id": update.message.from_user.id,
        "creation_date": datetime.utcnow()
    }

    result = bets_collection.insert_one(bet_data)
    
    if result.inserted_id:
        await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
    else:
        await update.message.reply_text("Failed to create bet. Please try again.")
    
    return ConversationHandler.END

# Function to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bet creation canceled.")
    return ConversationHandler.END

# Create the conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.CommandStart('create_bet'), start)],
    states={
        SELECT_SPORT: [CallbackQueryHandler(select_sport)],
        SELECT_MATCH: [CallbackQueryHandler(select_match)],
        SELECT_OUTCOME: [CallbackQueryHandler(select_outcome)],
        ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)]
    },
    fallbacks=[MessageHandler(filters.Regex('^/cancel$'), cancel)]
)
