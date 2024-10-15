import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from config import predefined_collection, bets_collection
from datetime import datetime

# Define stages
SELECT_SPORT, SELECT_MATCH, SELECT_OUTCOME, SELECT_AMOUNT = range(4)

# Set up logging
logger = logging.getLogger(__name__)

# Function to start bet creation
async def start(update: Update, context: CallbackContext) -> int:
    logger.info("User started bet creation process")
    
    # Fetch the list of sports from the predefined_collection
    sports = predefined_collection.distinct("sport")
    reply_keyboard = [[sport] for sport in sports]

    await update.message.reply_text(
        "Select Sport:", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECT_SPORT

# Function to handle sport selection
async def select_sport(update: Update, context: CallbackContext) -> int:
    selected_sport = update.message.text
    logger.info(f"Sport selected: {selected_sport}")

    # Store selected sport
    context.user_data["sport"] = selected_sport

    # Fetch the list of matches for the selected sport
    matches = predefined_collection.find({"sport": selected_sport}).distinct("match")
    reply_keyboard = [[match] for match in matches]

    await update.message.reply_text(
        "Select Match:", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECT_MATCH

# Function to handle match selection
async def select_match(update: Update, context: CallbackContext) -> int:
    selected_match = update.message.text
    logger.info(f"Match selected: {selected_match}")

    # Store selected match
    context.user_data["match"] = selected_match

    # Fetch the list of outcomes for the selected match
    outcomes = predefined_collection.find({"sport": context.user_data["sport"], "match": selected_match}).distinct("outcome")
    reply_keyboard = [[outcome] for outcome in outcomes]

    await update.message.reply_text(
        "Select Outcome:", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECT_OUTCOME

# Function to handle outcome selection
async def select_outcome(update: Update, context: CallbackContext) -> int:
    selected_outcome = update.message.text
    logger.info(f"Outcome selected: {selected_outcome}")

    # Store selected outcome
    context.user_data["outcome"] = selected_outcome

    await update.message.reply_text("Enter the amount: (1 to 100)")
    return SELECT_AMOUNT

# Function to handle bet amount
async def select_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text

    if not amount.isdigit() or not (1 <= int(amount) <= 100):
        await update.message.reply_text("Invalid amount. Enter a value between 1 and 100.")
        return SELECT_AMOUNT

    # Store amount
    context.user_data["amount"] = int(amount)
    
    # Save the bet to the bets_collection
    bet_data = {
        "sport": context.user_data["sport"],
        "match": context.user_data["match"],
        "outcome": context.user_data["outcome"],
        "amount": context.user_data["amount"],
        "user_id": update.message.from_user.id,
        "creation_date": datetime.now()
    }

    try:
        result = bets_collection.insert_one(bet_data)
        logger.info(f"Bet successfully saved to MongoDB: {bet_data}")
        await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to save bet to MongoDB: {e}")
        await update.message.reply_text("An error occurred while saving your bet. Please try again.")

    return ConversationHandler.END

# Function to cancel bet creation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Bet creation canceled.")
    return ConversationHandler.END

# Define conversation handler with states and handlers
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        SELECT_SPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_sport)],
        SELECT_MATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_match)],
        SELECT_OUTCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_outcome)],
        SELECT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_amount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
