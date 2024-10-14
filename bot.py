import logging
import firebase_admin
from firebase_admin import credentials, db
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import API_TOKEN
from handlers.create_bet_handler import create_bet_conv_handler
from handlers.start_handler import start
from handlers.view_bets_handler import view_bets
from handlers.accept_bet_handler import accept_bet
from handlers.calculate_result_handler import calculate_result

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase
cred = credentials.Certificate('path_to_your/firebase_key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://<your-project-id>.firebaseio.com/'
})

# Function to handle button clicks (unchanged)
async def button(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'create_bet':
        await query.message.reply_text("You clicked Create Bet! Please use the command /create_bet.")
    elif query.data == 'view_bets':
        await query.message.reply_text("You clicked View Bets! Please use the command /view_bets.")
    elif query.data == 'accept_bet':
        await query.message.reply_text("You clicked Accept Bet! Please use the command /accept_bet.")
    elif query.data == 'calculate_result':
        await query.message.reply_text("You clicked Calculate Result! Please use the command /calculate_result.")

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    logger.info("Bot is starting...")

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("view_bets", view_bets))
    app.add_handler(CommandHandler("accept_bet", accept_bet))
    app.add_handler(CommandHandler("calculate_result", calculate_result))
    app.add_handler(create_bet_conv_handler)

    app.run_polling()

if __name__ == '__main__':
    main()
