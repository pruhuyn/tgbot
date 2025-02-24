import sqlite3
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils import telegram

API_TOKEN = '8116355818:AAF3yBKLv4XpZn_-YqE7A5EeKVy905dNa0M'

# Инициализация бота и приложения
bot = Bot(token=API_TOKEN)
app = telegram.Application.builder().token(API_TOKEN).build()

# Определяем состояния
class Form(StatesGroup):
    username = State()

@app.message_handler(commands=["login"])
async def cmd_login(message: Message, state: FSMContext):
    await message.answer("Введите ваш username:")
    await Form.username.set()

@app.message_handler(state=Form.username)
async def check_username(message: Message, state: FSMContext):
    username_to_check = message.text

    # Подключение к базе данных
    conn = sqlite3.connect(r'C:\Users\Alexei\Desktop\tgbot\instance.users.db')  # Путь к базе данных
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM user WHERE username=?", (username_to_check,))
    user = cursor.fetchone()

    if user:
        await message.answer(f"Пользователь найден: {user[0]}")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")

    conn.close()
    await state.finish()  # Заканчиваем состояние

if __name__ == '__main__':
    app.run_polling()
