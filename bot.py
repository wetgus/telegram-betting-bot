from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler
from Handlers.menu_handler import start, help_command, cancel
from Handlers.create_bet_handler import create_bet, bet_description, bet_amount, view_bets, BET_DESCRIPTION, BET_AMOUNT
from config import API_TOKEN  # Import the API token from config.py

def main():
    updater = Updater(API_TOKEN, use_context=True)  # Use the token from config.py
    dp = updater.dispatcher

    # Start command handler
    dp.add_handler(CommandHandler('start', start))

    # Add conversation handler for bet creation
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Create Bet$'), create_bet)],
        states={
            BET_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, bet_description)],
            BET_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, bet_amount)],
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel)]
    )

    dp.add_handler(conv_handler)

    # Add other menu options
    dp.add_handler(MessageHandler(Filters.regex('^View Bets$'), view_bets))
    dp.add_handler(MessageHandler(Filters.regex('^Help$'), help_command))
    dp.add_handler(MessageHandler(Filters.regex('^Cancel$'), cancel))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
