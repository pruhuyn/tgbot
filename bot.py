import sqlite3
from aiogram import Bot, types
from aiogram.client import Application
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

API_TOKEN = '8116355818:AAF3yBKLv4XpZn_-YqE7A5EeKVy905dNa0M'

# Создаем бота и приложение
bot = Bot(token=API_TOKEN)
app = Application.builder().token(API_TOKEN).build()

# Описание состояний
class Form(StatesGroup):
    username = State()

# Команда для начала авторизации
@app.message_handler(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш username:")
    await Form.username.set()

# Обработка введенного username
@app.message_handler(state=Form.username)
async def check_username(message: types.Message, state: FSMContext):
    username_to_check = message.text

    # Подключение к базе данных
    conn = sqlite3.connect('C:\\Users\\Alexei\\Desktop\\tgbot\\instance.users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM user WHERE username=?", (username_to_check,))
    user = cursor.fetchone()

    if user:
        await message.answer(f"Пользователь найден: {user[0]}")
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")

    conn.close()
    await state.finish()

if __name__ == '__main__':
    app.run_polling()
