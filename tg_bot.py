import os
import sys
import django

# Настройка путей и окружения Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import telebot
from dotenv import load_dotenv
from users.models import Profile

# Загружаем токен из скрытого файла .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

print("Бот успешно запущен и слушает команды...")


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = str(message.chat.id)
    text_args = message.text.split()

    if len(text_args) > 1:
        auth_code = text_args[1]
        try:
            profile = Profile.objects.get(tg_auth_code=auth_code)
            profile.telegram_chat_id = chat_id
            profile.tg_auth_code = None
            profile.save()

            bot.reply_to(
                message,
                f"🎉 Успешно! Аккаунт {profile.user.username} привязан к Deadline Tracker.\n"
                f"Теперь я буду присылать тебе уведомления о приближающихся сроках задач!"
            )
        except Profile.DoesNotExist:
            bot.reply_to(message, "❌ Ошибка: Код привязки недействителен или устарел.")
    else:
        bot.reply_to(
            message,
            "Привет! Я бот Deadline Tracker.\n"
            "Чтобы я присылал тебе уведомления, зайди в свой Профиль на сайте, "
            "скопируй код привязки и нажми кнопку «Открыть бота»."
        )


if __name__ == '__main__':
    bot.infinity_polling()