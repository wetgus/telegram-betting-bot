from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION, PREDEFINED_COLLECTION

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]
bets_collection = db[MONGODB_COLLECTION]  # Collection for storing placed bets
predefined_collection = db[PREDEFINED_COLLECTION]  # Collection for fetching predefined markets

# States for conversation
SELECT_SPORT, SELECT_MATCH, SELECT_OUTCOME, ENTER_AMOUNT = range(4)

# Start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predefined_sports = predefined_collection.distinct("sport")
    
    keyboard = [[InlineKeyboardButton(sport, callback_data=sport)] for sport in predefined_sports]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Please select a sport:", reply_markup=reply_markup)
    return SELECT_SPORT

# Sport selection handler
async def select_sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    selected_sport = query.data
    context.user_data['sport'] = selected_sport

    predefined_matches = predefined_collection.distinct("match", {"sport": selected_sport})
    
    keyboard = [[InlineKeyboardButton(match, callback_data=match)] for match in predefined_matches]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"Sport selected: {selected_sport}\nPlease select a match:", reply_markup=reply_markup)
    return SELECT_MATCH

# Match selection handler
async def select_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    selected_match = query.data
    context.user_data['match'] = selected_match

    predefined_outcomes = predefined_collection.distinct("outcome", {"sport": context.user_data['sport'], "match": selected_match})
    
    keyboard = [[InlineKeyboardButton(outcome, callback_data=outcome)] for outcome in predefined_outcomes]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"Match selected: {selected_match}\nPlease select an outcome:", reply_markup=reply_markup)
    return SELECT_OUTCOME

# Outcome selection handler
async def select_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_outcome = query.data
    context.user_data['outcome'] = selected_outcome
    
    await query.edit_message_text(f"Outcome selected: {selected_outcome}\nPlease enter the amount (1 to 100):")
    return ENTER_AMOUNT

# Bet amount handler with validation
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_text = update.message.text

    if not amount_text.isdigit() or not (1 <= int(amount_text) <= 100):
        await update.message.reply_text("Invalid amount! Please enter a valid amount between 1 and 100.")
        return ENTER_AMOUNT

    bet_data = {
        "sport": context.user_data['sport'],
        "match": context.user_data['match'],
        "outcome": context.user_data['outcome'],
        "amount": amount_text,
        "user_id": update.message.from_user.id,
        "creation_date": datetime.utcnow(),
    }

    result = bets_collection.insert_one(bet_data)
    await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")

    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bet creation canceled.")
    return ConversationHandler.END

create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        SELECT_SPORT: [CallbackQueryHandler(select_sport)],
        SELECT_MATCH: [CallbackQueryHandler(select_match)],
        SELECT_OUTCOME: [CallbackQueryHandler(select_outcome)],
        ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
