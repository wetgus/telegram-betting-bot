from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import bets_collection
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define conversation states
SELECT_SPORT, SELECT_MATCH, SELECT_OUTCOME, ENTER_AMOUNT = range(4)

# Step 1: Start the conversation and show sports
async def start_create_bet(update: Update, context):
    logger.info("Starting bet creation process...")
    
    # Fetch sports from MongoDB
    sports = bets_collection.distinct("sport")
    
    # Create inline buttons for sports
    keyboard = [[InlineKeyboardButton(sport, callback_data=sport)] for sport in sports]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Select a sport:", reply_markup=reply_markup)
    
    return SELECT_SPORT

# Step 2: User selects sport, show matches
async def select_sport(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    sport = query.data
    context.user_data['selected_sport'] = sport
    
    # Fetch matches for the selected sport from MongoDB
    matches = bets_collection.find_one({"sport": sport})['matches']
    
    # Create inline buttons for matches
    keyboard = [[InlineKeyboardButton(match['name'], callback_data=match['name'])] for match in matches]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"Selected Sport: {sport}. Now, select a match:", reply_markup=reply_markup)
    
    return SELECT_MATCH

# Step 3: User selects match, show outcomes
async def select_match(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    match = query.data
    context.user_data['selected_match'] = match
    
    # Fetch outcomes for the selected match from MongoDB
    selected_sport = context.user_data['selected_sport']
    matches = bets_collection.find_one({"sport": selected_sport})['matches']
    outcomes = next(m['outcomes'] for m in matches if m['name'] == match)
    
    # Create inline buttons for outcomes
    keyboard = [[InlineKeyboardButton(outcome, callback_data=outcome)] for outcome in outcomes]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"Selected Match: {match}. Now, select an outcome:", reply_markup=reply_markup)
    
    return SELECT_OUTCOME

# Step 4: User selects outcome, ask for bet amount
async def select_outcome(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    outcome = query.data
    context.user_data['selected_outcome'] = outcome
    
    await query.edit_message_text(f"Selected Outcome: {outcome}. Now, enter the bet amount (1 to 100):")
    
    return ENTER_AMOUNT

# Step 5: User enters bet amount, validate and save the bet
async def enter_amount(update: Update, context):
    amount_text = update.message.text
    
    # Validate amount
    if not amount_text.isdigit() or not (1 <= int(amount_text) <= 100):
        await update.message.reply_text("Invalid amount. Please enter a number between 1 and 100.")
        return ENTER_AMOUNT
    
    amount = int(amount_text)
    context.user_data['bet_amount'] = amount
    
    # Save bet to MongoDB
    bet_data = {
        "user_id": update.message.from_user.id,
        "sport": context.user_data['selected_sport'],
        "match": context.user_data['selected_match'],
        "outcome": context.user_data['selected_outcome'],
        "amount": amount,
        "creation_date": datetime.utcnow()
    }
    result = bets_collection.insert_one(bet_data)
    
    await update.message.reply_text(f"Bet created successfully! BetID: {result.inserted_id}")
    
    return ConversationHandler.END

# Conversation handler with states
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start_create_bet)],
    states={
        SELECT_SPORT: [CallbackQueryHandler(select_sport)],
        SELECT_MATCH: [CallbackQueryHandler(select_match)],
        SELECT_OUTCOME: [CallbackQueryHandler(select_outcome)],
        ENTER_AMOUNT: [MessageHandler(filters.TEXT, enter_amount)]
    },
    fallbacks=[]
)
