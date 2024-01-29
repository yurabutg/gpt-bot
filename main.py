import os
from openai import OpenAI
from dotenv import load_dotenv
import telebot
import logging

# Define the directory for user logs
logs_directory = 'users_logs'

# Configure the root logger only once
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')

# Create the logs' directory if it doesn't exist
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)


# Function to get the filename for user logs
def get_user_log_filename(username):
    return os.path.join(logs_directory, f"{username}.log")


# Load environment variables
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')

# Initialize the OpenAI and Telegram bot instances
gpt = OpenAI()
bot = telebot.TeleBot(token)
bot_username = bot.get_me().username
bot_first_name = bot.get_me().first_name


# Function to log user messages and bot responses
def log_message(username, message, response):
    log_filename = get_user_log_filename(username)
    logger = logging.getLogger(username)
    file_handler = logging.FileHandler(log_filename)

    logger.addHandler(file_handler)
    logger.warning(f"Received message from {username}: {message} \n Response: {response}")
    logger.removeHandler(file_handler)


# Handle messages mentioning the bot first name
@bot.message_handler(func=lambda message: bot_first_name.lower() in message.text.lower())
def handle_mention(message):
    username = message.from_user.username

    # Generate completion using OpenAI GPT-3.5-turbo
    completion = gpt.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message.text}
        ]
    )

    # Get the response from the completion
    response = completion.choices[0].message

    # Reply to the user and log the message and response
    bot.reply_to(message, response.content)
    log_message(username, message.text, response.content)


# Start the bot polling
if __name__ == "__main__":
    bot.polling(none_stop=True)
