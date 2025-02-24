import asyncio
import os
from aiogram import Bot, Dispatcher, types

# Токен бота берём из переменных Railway
TOKEN = os.getenv("TOKEN")

# Проверка токена
if not TOKEN:
    raise ValueError("Нет токена! Добавь его в Railway.")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Я работаю на Railway! 🚀")

# Команда /help
@dp.message(lambda message: message.text == "/help")
async def help(message: types.Message):
    await message.answer("Доступные команды:\n/start - Запустить бота\n/help - Помощь")

# Обработчик любых сообщений (эхо-бот)
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ты сказал: {message.text}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
