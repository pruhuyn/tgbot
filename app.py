from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Инициализация приложения
app = Flask(__name__)

# Настройка базы данных
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

# Стартовая страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница регистрации
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

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
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

# Запуск приложения
if __name__ == "__main__":
    # Создание базы данных (если она не существует)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
