from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers.menu_handler import start, help_command, cancel
from handlers.create_bet_handler import create_bet, bet_description, bet_amount, view_bets, BET_DESCRIPTION, BET_AMOUNT
from config import API_TOKEN  # Import the API token from config.py

def main():
    # Create the Application object
    application = ApplicationBuilder().token(API_TOKEN).build()  # Use the token from config.py

    # Start command handler
    application.add_handler(CommandHandler('start', start))

    # Add conversation handler for bet creation
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Create Bet$'), create_bet)],
        states={
            BET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bet_description)],
            BET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bet_amount)],
        },
        fallbacks=[MessageHandler(filters.Regex('^Cancel$'), cancel)]
    )

    application.add_handler(conv_handler)

    # Add other menu options
    application.add_handler(MessageHandler(filters.Regex('^View Bets$'), view_bets))
    application.add_handler(MessageHandler(filters.Regex('^Help$'), help_command))
    application.add_handler(MessageHandler(filters.Regex('^Cancel$'), cancel))

    application.run_polling()  # Start polling for updates

if __name__ == '__main__':
    main()
