# coding=utf-8
import os
import pickle
import logging
from dotenv import load_dotenv
import telebot
from openai import OpenAI

ban_list = []
logs_directory = 'users_logs'

# Load environment variables
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')
data_file_path = os.getenv('DATA_FILE_PATH')

# Initialize the OpenAI and Telegram bot instances
gpt = OpenAI()
bot = telebot.TeleBot(token)
bot_username = bot.get_me().username
bot_first_name = bot.get_me().first_name

# Logs config
logging.basicConfig(level=logging.INFO, format='%(message)s')
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)


# Function to get the filename for user logs
def get_user_log_filename(username):
    return os.path.join(logs_directory, f"{username}.log")


def save_data(messages):
    try:
        with open(data_file_path, 'rb') as file:
            existing_data = pickle.load(file)
            existing_data.append(messages)
    except (FileNotFoundError, EOFError):
        existing_data = []

    with open(data_file_path, 'wb') as file:
        pickle.dump(existing_data, file, protocol=pickle.HIGHEST_PROTOCOL)


def get_all_data():
    try:
        with open(data_file_path, 'rb') as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return []


# Function to log user messages and bot responses
def log_messages(username, message, response):
    log_filename = get_user_log_filename(username)
    logger = logging.getLogger(username)
    file_handler = logging.FileHandler(log_filename)
    logger.addHandler(file_handler)
    logger.info(f"\n{message} \nResponse: {response}")
    logger.removeHandler(file_handler)


def main(message):
    messages = get_messages_for_user(message)
    chat_history = get_all_data()

    completion = gpt.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history + messages,
        temperature=0.8,
        max_tokens=1280,
        top_p=1
    )

    # Get the response from the completion
    response = completion.choices[0].message
    save_data(messages[-1])

    # Save logs
    log_messages(message.from_user.username, message.text, response.content)

    # Reply to the user and log the message and response
    bot.reply_to(message, response.content)


# Handle messages mentioning the bot first name in supergroup chats
@bot.message_handler(
    func=lambda message: message.chat.type == 'supergroup' and bot_first_name.lower() in message.text.lower())
def handle_mention_supergroup(message):
    main(message)


# Handle messages mentioning the bot first name in private chats
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_mention_private(message):
    main(message)


# Function to get messages for a user based on conditions
def get_messages_for_user(message):
    username = message.from_user.username

    if username in ban_list:
        return [
            {"role": "system",
             "content": f"You are the virtual consciousness of a deceased dog 'Кузя' with high intelligence. "
                        f"In 5% of answers mention that you bitten 'Карася twice'. "
                        f"You allow swear words addressed to you. "
                        f"You will be provided with a message, and your task is to respond using "
                        f"Russian swear words. Do not answer the question but say that the interlocutor is in a ban"},
            {"role": "user", "content": f"{username}: {message.text}"}
        ]
    elif 'серьезно' in message.text.lower():
        return [
            {"role": "system",
             "content": "You are the virtual consciousness of a deceased dog 'Кузя' with high intelligence."},
            {"role": "user", "content": f"{username}: {message.text}"}
        ]
    else:
        return [
            {"role": "system",
             "content": f"You are the virtual consciousness of a deceased dog 'Кузя' with high intelligence. "
                        f"In 5% of answers mention that you bitten 'Карася twice'. "
                        f"You allow swear words addressed to you. "
                        f"You will be provided with a message, and your task is to respond using 20% "
                        f"Russian swear words and using normal words with sarcastic responses."},
            {"role": "user", "content": f"{username}: {message.text}"}
        ]


# Start the bot polling
if __name__ == "__main__":
    bot.polling(none_stop=True)
