import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Токен бота берём из переменных Railway
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Нет токена! Добавь его в Railway.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Заглушка для базы данных
# Это можно заменить на реальную базу данных, например, SQLite
users_db = {
    "admin": {"password": "adminpass", "is_logged_in": False}
}

# Команда /start
@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогу тебе с авторизацией. Введи /login для входа.")

# Команда /login
@dp.message(lambda message: message.text.startswith("/login"))
async def login(message: types.Message):
    user_id = message.from_user.id
    # Если пользователь уже авторизован
    if users_db.get(str(user_id), {}).get("is_logged_in", False):
        await message.answer("Вы уже авторизованы!")
        return

    await message.answer("Введите имя пользователя:")

    @dp.message(lambda message: True)
    async def ask_username(msg: types.Message):
        username = msg.text
        await msg.answer(f"Теперь введите пароль для {username}:")
        
        @dp.message(lambda message: True)
        async def ask_password(pwd_msg: types.Message):
            password = pwd_msg.text
            
            # Проверка введенных данных
            user_data = users_db.get(username)
            if user_data and user_data["password"] == password:
                users_db[str(msg.from_user.id)] = {"password": password, "is_logged_in": True}
                await pwd_msg.answer(f"Добро пожаловать, {username}!")
            else:
                await pwd_msg.answer("Неверный логин или пароль! Попробуйте снова.")
                return

# Обработчик любых сообщений (эхо-бот)
@dp.message()
async def echo(message: types.Message):
    user_id = message.from_user.id
    if users_db.get(str(user_id), {}).get("is_logged_in", False):
        await message.answer(f"Ты сказал: {message.text}")
    else:
        await message.answer("Вы не авторизованы! Для доступа используйте команду /login.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
