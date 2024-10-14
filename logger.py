import logging
from logging.handlers import RotatingFileHandler

# Set up the logger
logger = logging.getLogger('telegram_bot')
logger.setLevel(logging.DEBUG)

# Create file handler with log rotation
file_handler = RotatingFileHandler('bot.log', maxBytes=2000000, backupCount=5)
file_handler.setLevel(logging.DEBUG)

# Create console handler for output to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
