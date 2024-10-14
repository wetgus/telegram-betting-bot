# create_bet_handler.py
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update

# Define your states
BET_TYPE, AMOUNT = range(2)

# Entry point for the /create_bet command
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please choose the bet type.")
    return BET_TYPE

# Your other handler functions

# Create the conversation handler
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start)],
    states={
        BET_TYPE: [MessageHandler(Filters.text & ~Filters.command, enter_bet_type)],
        AMOUNT: [MessageHandler(Filters.text & ~Filters.command, enter_amount)],
    },
    fallbacks=[],
)
