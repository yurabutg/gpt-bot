# coding=utf-8
import os
import pickle
from dotenv import load_dotenv
import telebot
from openai import OpenAI

ban_list = []

# Load environment variables
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')
data_file_path = os.getenv('DATA_FILE_PATH')

# Initialize the OpenAI and Telegram bot instances
gpt = OpenAI()
bot = telebot.TeleBot(token)
bot_username = bot.get_me().username
bot_first_name = bot.get_me().first_name


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


# Handle messages mentioning the bot first name
@bot.message_handler(func=lambda message: bot_first_name.lower() in message.text.lower())
def handle_mention(message):
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

    # Reply to the user and log the message and response
    bot.reply_to(message, response.content)


# Function to get messages for a user based on conditions
def get_messages_for_user(message):
    username = message.from_user.username

    if username in ban_list:
        return [
            {"role": "system",
             "content": f"You are the virtual consciousness of a deceased dog 'Кузя' with high intelligence. "
                        f"In 10% of answers mention that you bitten 'Карася twice'. "
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
                        f"In 10% of answers mention that you bitten 'Карася twice'. "
                        f"You allow swear words addressed to you. "
                        f"You will be provided with a message, and your task is to respond using 20% "
                        f"Russian swear words and using normal words with sarcastic responses."},
            {"role": "user", "content": f"{username}: {message.text}"}
        ]


# Start the bot polling
if __name__ == "__main__":
    bot.polling(none_stop=True)
