from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from config import ADMIN_USER_ID

# Define states for the conversation
DESCRIPTION, DATE = range(2)

# Start conversation by asking for bet description
def start_create_bet(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please provide the description of the bet.")
    return DESCRIPTION

# Save description and ask for the bet date
def received_description(update: Update, context: CallbackContext) -> int:
    context.user_data['description'] = update.message.text
    update.message.reply_text("Please provide the date for the bet (YYYY-MM-DD).")
    return DATE

# Save date, create the bet, and confirm the creation
def received_date(update: Update, context: CallbackContext) -> int:
    description = context.user_data.get('description')
    date = update.message.text
    bet_id = create_bet_in_database(description, date)  # This function will handle database saving
    
    update.message.reply_text(f"Bet created! ID: {bet_id}")
    return ConversationHandler.END

# Fallback function in case user cancels or input is invalid
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Bet creation cancelled.")
    return ConversationHandler.END

# Dummy function to store bet in the database
def create_bet_in_database(description, date):
    # Logic for saving the bet in the database
    # Return a unique bet ID (dummy example)
    return 1  # Replace this with actual ID generation logic

# Update your start command to reflect the new flow
def start(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['Create Bet', 'View Bets'], ['Cancel']]
    update.message.reply_text(
        'Please choose an option:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

# Handle user button clicks
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'Create Bet':
        # Trigger the conversation flow directly
        context.bot.send_message(chat_id=update.effective_chat.id, text="/create_bet")

def main() -> None:
    # Other initializations
    updater = Updater("YOUR_TOKEN_HERE", use_context=True)
    dispatcher = updater.dispatcher

    # Add the ConversationHandler for the "Create Bet" flow
    create_bet_handler = ConversationHandler(
        entry_points=[CommandHandler('create_bet', start_create_bet)],
        states={
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, received_description)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, received_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Register the handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(create_bet_handler)
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
