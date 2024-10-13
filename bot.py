from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Dictionary to hold bets
bets = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the betting bot! Use /create_bet to start.")

# Create bet command handler
async def create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /create_bet <bet_description> <end_date>")
        return
    
    bet_description = context.args[0]
    end_date = context.args[1]  # You can add date validation later
    bet_id = len(bets) + 1  # Simple ID assignment
    
    bets[bet_id] = {
        'description': bet_description,
        'end_date': end_date,
        'user_bets': {}
    }
    
    await update.message.reply_text(f"Bet created with ID: {bet_id}")

# Accept bet command handler
async def accept_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /accept_bet <bet_id> <your_bet>")
        return
    
    bet_id = int(context.args[0])
    user_bet = context.args[1]
    
    if bet_id not in bets:
        await update.message.reply_text("Bet ID does not exist.")
        return
    
    bets[bet_id]['user_bets'][update.effective_user.username] = user_bet
    await update.message.reply_text(f"You have accepted the bet {bet_id} with your prediction: {user_bet}")

# Calculate result command handler
async def calculate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /calculate_result <bet_id> <actual_result>")
        return
    
    bet_id = int(context.args[0])
    actual_result = context.args[1]
    
    if bet_id not in bets:
        await update.message.reply_text("Bet ID does not exist.")
        return
    
    # Determine the outcome
    winners = []
    for user, prediction in bets[bet_id]['user_bets'].items():
        if prediction == actual_result:
            winners.append(user)

    if winners:
        await update.message.reply_text(f"The winners for bet {bet_id} are: {', '.join(winners)}")
    else:
        await update.message.reply_text(f"No winners for bet {bet_id}.")

# Main function to run the bot
def main():
    api_token = 'YOUR_API_TOKEN'  # Replace with your actual API token
    app = ApplicationBuilder().token(api_token).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_bet", create_bet))
    app.add_handler(CommandHandler("accept_bet", accept_bet))
    app.add_handler(CommandHandler("calculate_result", calculate_result))

    app.run_polling()

if __name__ == '__main__':
    main()
