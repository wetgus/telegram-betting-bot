import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import API_TOKEN
from handlers.start_handler import start
from handlers.create_bet_handler import create_bet
from handlers.view_bets_handler import view_bets
from handlers.accept_bet_handler import accept_bet
from handlers.calculate_result_handler import calculate_result

# Initialize global variable to store bets
bets = {}

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Handle the button clicks
    if query.data == 'create_bet':
        await create_bet(update, context)  # Call the create_bet function directly
    elif query.data == 'view_bets':
        await view_bets(update, context)  # Call the view_bets function directly
    elif query.data == 'accept_bet':
        await accept_bet(update, context)  # Call the accept_bet function directly
    elif query.data == 'calculate_result':
        await calculate_result(update, context)  # Call the calculate_result function directly


# Main function to run the bot
def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    
    logger.info("Bot is starting...")  # Log when the bot starts
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))  # Register callback query handler
    app.add_handler(CommandHandler("create_bet", create_bet))
    app.add_handler(CommandHandler("view_bets", view_bets))  # Add view_bets handler
    app.add_handler(CommandHandler("accept_bet", accept_bet))
    app.add_handler(CommandHandler("calculate_result", calculate_result))

    app.run_polling()

if __name__ == '__main__':
    main()
