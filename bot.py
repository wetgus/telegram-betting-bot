import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import API_TOKEN
from handlers.create_bet_handler import create_bet_conv_handler  # Keep this import only
from handlers.start_handler import start
from handlers.view_bets_handler import view_bets
from handlers.accept_bet_handler import accept_bet
from handlers.calculate_result_handler import calculate_result

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle button clicks
async def button(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'create_bet':
        # Send a command that initiates the conversation
        await context.bot.send_message(chat_id=query.message.chat_id, text="/create_bet")
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
    app.add_handler(create_bet_conv_handler)  # This is correct

    app.run_polling()

if __name__ == '__main__':
    main()
