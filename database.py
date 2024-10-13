import json
import os

DB_FILE = 'bets.json'

# Initialize the JSON file if it doesn't exist
def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"bets": []}, f)

# Function to load all bets from the JSON file
def load_bets():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

# Function to save bets to the JSON file
def save_bets(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Function to create a new bet and save it in the JSON file
def create_bet(description, date):
    data = load_bets()
    new_bet = {
        "id": len(data['bets']) + 1,  # Assign a simple incremental ID
        "description": description,
        "date": date
    }
    data['bets'].append(new_bet)
    save_bets(data)
    return new_bet['id']
