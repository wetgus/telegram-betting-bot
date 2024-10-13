from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Function to handle the /start command
async def start(update: Update, context):
    await update.message.reply_text("Hello! I am a betting bot.")

# Main function to run the bot
def main():
    api_token = 'YOUR_API_TOKEN'  # Replace with your actual API token
    app = ApplicationBuilder().token(api_token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
