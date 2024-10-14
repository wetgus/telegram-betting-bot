import json
import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes

bets_file = "bets.json"

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

# Dictionary to store user input states
user_state = {}

async def create_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    if user_id not in user_state:
        # Step 1: Ask for the bet description with validation guidelines
        await update.message.reply_text(
            "Please enter the bet description (1 to 200 characters):"
        )
        user_state[user_id] = {"step": "awaiting_description"}
        return

    if user_state[user_id]["step"] == "awaiting_description":
        # Step 2: Validate the description
        if len(message) < 1 or len(message) > 200:
            await update.message.reply_text(
                "Invalid description. Please ensure the description is between 1 and 200 characters."
            )
            return

        # Store the description and ask for the amount with validation guidelines
        user_state[user_id]["description"] = message
        user_state[user_id]["step"] = "awaiting_amount"
        await update.message.reply_text("Please enter the bet amount (integer between 1 and 100):")
        return

    if user_state[user_id]["step"] == "awaiting_amount":
        # Step 3: Validate the amount
        try:
            amount = int(message)
            if amount < 1 or amount > 100:
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "Invalid amount. Please enter a whole number between 1 and 100."
            )
            return

        # Generate unique bet ID
        bet_id = str(uuid.uuid4())
        bet_description = user_state[user_id]["description"]

        # Create a bet record
        bet = {
            "bet_id": bet_id,
            "description": bet_description,
            "amount": amount,
            "date": update.message.date.isoformat(),
            "user_id": user_id,
            "username": update.message.from_user.username
        }

        # Save the bet to the JSON file
        write_bet(bet)

        # Acknowledge the user
        await update.message.reply_text(
            f'Bet "{bet_description}" is accepted with {amount} on stake; your bet ID is "{bet_id}".'
        )

        # Clear user state
        del user_state[user_id]
