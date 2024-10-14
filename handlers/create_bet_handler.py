import uuid
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from firebase_admin import db

# Define states for ConversationHandler
DESCRIPTION, AMOUNT = range(2)

# Function to write bets to Firebase
def write_bet_to_firebase(bet):
    ref = db.reference('bets')
    ref.push(bet)

# Function to start the bet creation process
async def start_create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter the bet description (1 to 200 characters):"
    )
    return DESCRIPTION

# Function to handle bet description input
async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    if len(description) < 1 or len(description) > 200:
        await update.message.reply_text("Invalid description. Please enter between 1 and 200 characters.")
        return DESCRIPTION
    context.user_data['description'] = description
    await update.message.reply_text("Please enter the bet amount (integer between 1 and 100):")
    return AMOUNT

# Function to handle bet amount input and save to Firebase
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text)
        if amount < 1 or amount > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid amount. Enter a number between 1 and 100.")
        return AMOUNT

    description = context.user_data['description']
    bet_id = str(uuid.uuid4())
    user_id = update.message.from_user.id

    bet = {
        "bet_id": bet_id,
        "description": description,
        "amount": amount,
        "date": update.message.date.isoformat(),
        "user_id": user_id,
        "username": update.message.from_user.username
    }

    # Save the bet to Firebase
    write_bet_to_firebase(bet)

    # Acknowledge the user
    await update.message.reply_text(
        f'Bet "{description}" is accepted with {amount} on stake; your bet ID is "{bet_id}".'
    )

    return ConversationHandler.END

# Function to cancel the bet creation process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bet creation process canceled.")
    return ConversationHandler.END

# Create the ConversationHandler to manage the conversation flow
create_bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_bet', start_create_bet)],
    states={
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_description)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
