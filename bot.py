import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота из переменных окружения
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Нет токена! Добавь его в переменные окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных пользователей (используй свою БД)
users_db = {
    "admin": {"password": "adminpass", "is_logged_in": False}
}

# Стейт для обработки состояний
class Form:
    username = None
    waiting_for_username = False
    waiting_for_password = False

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Я бот. Чтобы начать, используй команду /login.")

# Команда /login
@dp.message(Command("login"))
async def login(message: Message):
    user_id = message.from_user.id
    
    # Проверка, авторизован ли пользователь
    if users_db.get(str(user_id), {}).get("is_logged_in", False):
        await message.answer("Вы уже авторизованы!")
        return
    
    Form.waiting_for_username = True
    await message.answer("Введите имя пользователя:")

# Ответ на ввод имени пользователя
@dp.message(F.text)
async def process_username(message: Message):
    if Form.waiting_for_username:
        username = message.text.strip()
        
        # Проверка на существующего пользователя
        if username not in users_db:
            await message.answer("Пользователь не найден. Попробуйте снова.")
            return
        
        Form.username = username
        Form.waiting_for_username = False
        Form.waiting_for_password = True

        await message.answer(f"Теперь введите пароль для пользователя {username}:")

# Ответ на ввод пароля
@dp.message(F.text)
async def process_password(message: Message):
    if Form.waiting_for_password:
        password = message.text.strip()
        
        if Form.username is None:
            await message.answer("Сначала введите имя пользователя!")
            return
        
        user_data = users_db.get(Form.username)

        # Проверка пароля
        if user_data and user_data["password"] == password:
            users_db[str(message.from_user.id)] = {"password": password, "is_logged_in": True}
            Form.waiting_for_password = False
            Form.username = None
            await message.answer(f"Добро пожаловать, {Form.username}!")
        else:
            await message.answer("Неверный пароль! Попробуйте снова.")
            Form.waiting_for_password = False
            Form.username = None

# Команда /logout
@dp.message(Command("logout"))
async def logout(message: Message):
    user_id = message.from_user.id
    if users_db.get(str(user_id), {}).get("is_logged_in", False):
        users_db[str(user_id)]["is_logged_in"] = False
        await message.answer("Вы вышли из системы.")
    else:
        await message.answer("Вы не авторизованы!")

# Обработчик любого сообщения
@dp.message()
async def echo(message: Message):
    user_id = message.from_user.id
    if users_db.get(str(user_id), {}).get("is_logged_in", False):
        await message.answer(f"Вы сказали: {message.text}")
    else:
        await message.answer("Вы не авторизованы! Для доступа используйте команду /login.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
