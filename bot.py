import asyncio
import os
from aiogram import Bot, Dispatcher, types
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Flask настройка базы данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Файл базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем отслеживание изменений
db = SQLAlchemy(app)

# Модель User для базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Telegram bot настройка
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Нет токена! Добавь его в Railway.")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Проверка логина
logged_in_users = set()  # Храним авторизованных пользователей

# Команда /start
@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Я работаю на Railway! 🚀")
    
# Команда /help
@dp.message(lambda message: message.text == "/help")
async def help(message: types.Message):
    await message.answer("Доступные команды:\n/start - Запустить бота\n/help - Помощь")

# Команда /login
@dp.message(lambda message: message.text.startswith("/login"))
async def login(message: types.Message):
    # Проверка, авторизован ли пользователь
    if message.from_user.id in logged_in_users:
        await message.answer("Вы уже авторизованы!")
        return
    
    await message.answer("Введите ваше имя пользователя:")

    @dp.message(lambda msg: msg.from_user.id == message.from_user.id)
    async def ask_password(msg: types.Message):
        username = msg.text
        user = User.query.filter_by(username=username).first()

        if user:
            await msg.answer(f"Пароль для {username}:")
            
            @dp.message(lambda msg: msg.from_user.id == message.from_user.id)
            async def verify_password(password_msg: types.Message):
                password = password_msg.text
                user = User.query.filter_by(username=username).first()
                
                if user and user.password == password:
                    logged_in_users.add(msg.from_user.id)  # Добавляем в список авторизованных
                    await password_msg.answer(f"Привет, {username}! Ты успешно авторизовался!")
                else:
                    await password_msg.answer("Неверный пароль!")
        else:
            await msg.answer("Пользователь не найден!")

# Обработчик любых сообщений (эхо-бот)
@dp.message()
async def echo(message: types.Message):
    if message.from_user.id not in logged_in_users:
        await message.answer("Вы не авторизованы! Для доступа используйте команду /login")
    else:
        await message.answer(f"Ты сказал: {message.text}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

# Запуск приложения Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Проверка на наличие такого пользователя
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Пользователь с таким именем уже существует!'
        
        # Создание нового пользователя
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))  # Перенаправляем на страницу логина после регистрации

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Поиск пользователя по имени
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return 'Успешный вход!'
        else:
            return 'Неверное имя пользователя или пароль!'
    
    return render_template('login.html')

# Запуск приложения Flask
if __name__ == "__main__":
    # Создание базы данных (если она не существует)
    with app.app_context():
        db.create_all()

    asyncio.run(main())  # Запускаем бота
    app.run(debug=True)  # Запускаем Flask приложение
