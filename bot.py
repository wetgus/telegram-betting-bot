import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

from handlers.create_bet_handler import create_bet, handle_bet_details
from handlers.view_bets_handler import view_bets
from handlers.accept_bet_handler import accept_bet
from handlers.calculate_result_handler import calculate_result

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for the conversation
WAITING_FOR_BET_DETAILS = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and show available commands."""
    keyboard = [
        [
            InlineKeyboardButton("Create Bet", callback_data='create_bet'),
            InlineKeyboardButton("View Bets", callback_data='view_bets'),
        ],
        [
            InlineKeyboardButton("Accept Bet", callback_data='accept_bet'),
            InlineKeyboardButton("Calculate Result", callback_data='calculate_result'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "I am Atlaslive Sportsbook bot. Let's explore my functions.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    try:
        if query.data == 'create_bet':
            await create_bet(update, context)  # Call the create_bet function directly
        elif query.data == 'view_bets':
            await view_bets(update, context)  # Call the view_bets function directly
        elif query.data == 'accept_bet':
            await accept_bet(update, context)  # Call the accept_bet function directly
        elif query.data == 'calculate_result':
            await calculate_result(update, context)  # Call the calculate_result function directly
    except Exception as e:
        logger.error(f"Error processing button click: {e}")  # Log the error
        await query.message.reply_text("An error occurred. Please try again.")

# Entry point to start the bot
if __name__ == '__main__':
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Set up the command handlers
    application.add_handler(CommandHandler("start", start))

    # Set up button handlers
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until you press Ctrl-C
    application.run_polling()
