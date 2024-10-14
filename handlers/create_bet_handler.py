# create_bet_handler.py
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update

# Define your states
BET_TYPE, AMOUNT = range(2)

# Entry point for the /create_bet command
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please choose the bet type.")
    return BET_TYPE

# Function to handle bet type selection
async def enter_bet_type(update: Update, context: CallbackContext) -> int:
    bet_type = update.message.text
    context.user_data['bet_type'] = bet_type  # Save bet type to user data
    await update.message.reply_text(f"You selected {bet_type}. Now please enter the amount.")
    return AMOUNT

# Function to handle entering the amount
async def enter_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    bet_type = context.user_data.get('bet_type')
    # Logic to save bet_type and amount to MongoDB should go here
    await update.message.reply_text(f"Bet created: Type - {bet_type}, Amount - {amount}.")
    return ConversationHandler.END

# Create the conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        BET_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bet_type)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
    },
    fallbacks=[],
)
