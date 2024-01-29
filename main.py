import os
from openai import OpenAI
from dotenv import load_dotenv
import telebot

load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')

gpt = OpenAI()
bot = telebot.TeleBot(token)
bot_username = bot.get_me().username
bot_first_name = bot.get_me().first_name

print(bot.get_me())

@bot.message_handler(func=lambda message: bot_first_name.lower() in message.text.lower())
def handle_mention(message):
    completion = gpt.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message.text}
        ]
    )

    response = completion.choices[0].message
    bot.reply_to(message, response.content)


if __name__ == "__main__":
    bot.polling(none_stop=True)
