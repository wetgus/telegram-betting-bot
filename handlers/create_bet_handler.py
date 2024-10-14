import json
import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

bets_file = "bets.json"

# Define states for ConversationHandler
DESCRIPTION, AMOUNT = range(2)

# Check if bets.json exists, if not create it
if not os.path.exists(bets_file):
    with open(bets_file, 'w') as f:
        json.dump([], f)

# Function to read bets from the JSON file
def read_bets():
    with open(bets_file, 'r') as f:
        return json.load(f)

# Function to write a new bet to the JSON file
def write_bet(bet):
    bets = read_bets()
    bets.append(bet)
    with open(bets_file, 'w') as f:
        json.dump(bets, f, indent=4)

async def start_create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the bet creation process."""
    await update.message.reply_text(
        "Please enter the bet description (1 to 200 characters):"
    )
    return DESCRIPTION

async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validates the bet description and asks for the bet amount."""
    description = update.message.text

    if len(description) < 1 or len(description) > 200:
        await update.message.reply_text(
            "Invalid description. Please ensure the description is between 1 and 200 characters."
        )
        return DESCRIPTION

    context.user_data['description'] = description
    await update.message.reply_text("Please enter the bet amount (integer between 1 and 100):")
    return AMOUNT

async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validates the bet amount, saves the bet, and confirms with the user."""
    try:
        amount = int(update.message.text)
        if amount < 1 or amount > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Invalid amount. Please enter a whole number between 1 and 100."
        )
        return AMOUNT

    description = context.user_data['description']
    bet_id = str(uuid.uuid4())
    user_id = update.message.from_user.id

    # Create the bet record
    bet = {
        "bet_id": bet_id,
        "description": description,
        "amount": amount,
        "date": update.message.date.isoformat(),
        "user_id": user_id,
        "username": update.message.from_user.username
    }

    # Save to JSON file
    write_bet(bet)

    # Acknowledge the user
    await update.message.reply_text(
        f'Bet "{description}" is accepted with {amount} on stake; your bet ID is "{bet_id}".'
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the bet creation process."""
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
