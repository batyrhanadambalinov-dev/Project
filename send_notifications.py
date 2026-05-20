import os
import sys
import django

# Настройка окружения Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import telebot
from dotenv import load_dotenv
from users.models import Task, Profile

# Загружаем токен из скрытого файла .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


def check_and_send_deadlines():
    print("--- ПРОВЕРКА ДЕДЛАЙНОВ ПО СВОЙСТВУ DAYS_LEFT ---")

    # Загружаем только невыполненные задачи
    active_tasks = Task.objects.filter(completed=False)

    burning_tasks = []
    for task in active_tasks:
        # Если до дедлайна остался ровно 1 день
        if task.days_left == 1:
            burning_tasks.append(task)

    if not burning_tasks:
        print("Задач со сроком сдачи на завтра (days_left == 1) не найдено.")
        return

    print(f"Найдено «горящих» задач: {len(burning_tasks)}")
    print("--- НАЧАЛО ОТПРАВКИ ---")

    for task in burning_tasks:
        user = task.user
        try:
            profile = Profile.objects.get(user=user)
            if profile.telegram_chat_id:
                message_text = (
                    f"⏰ **Внимание, дедлайн близко!**\n\n"
                    f"Напоминаем, что завтра заканчивается срок по задаче:\n"
                    f"📘 **{task.title}** (Предмет: {task.subject})\n\n"
                    f"Поспеши, чтобы успеть всё сдать вовремя! 💪"
                )

                bot.send_message(chat_id=profile.telegram_chat_id, text=message_text, parse_mode="Markdown")
                print(f"✓ Уведомление по задаче '{task.title}' успешно отправлено пользователю {user.username}.")
            else:
                print(f"⚠ У пользователя {user.username} есть задача на завтра, но его Telegram не привязан.")
        except Profile.DoesNotExist:
            print(f"⚠ Профиль для пользователя {user.username} не найден в базе.")


if __name__ == "__main__":
    check_and_send_deadlines()