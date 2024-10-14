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

    logger.info(f"User {query.from_user.username} clicked a button: {query.data}")  # Log button click

    # Handle the button clicks
    try:
        if query.data == 'create_bet':
            await query.message.reply_text("You clicked Create Bet! Please use the command /create_bet.")
        elif query.data == 'view_bets':
            await query.message.reply_text("You clicked View Bets! Please use the command /view_bets.")
        elif query.data == 'accept_bet':
            await query.message.reply_text("You clicked Accept Bet! Please use the command /accept_bet.")
        elif query.data == 'calculate_result':
            await query.message.reply_text("You clicked Calculate Result! Please use the command /calculate_result.")
        logger.info(f"Handled button action: {query.data}")
    except Exception as e:
        logger.error(f"Error processing button click {query.data}: {str(e)}")

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
    app.add_handler(create_bet_conv_handler)

    try:
        app.run_polling()
        logger.info("Bot is running...")
    except Exception as e:
        logger.error(f"Bot encountered an error: {str(e)}")

if __name__ == '__main__':
    main()
