from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# Функция для загрузки пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Функция для поиска пользователя по email
def find_user_by_email(email):
    return User.query.filter_by(email=email).first()

@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', errors={}, email='')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        errors = {}
        
        if not email:
            errors['email'] = 'Поле обязательно для заполнения!'
        if not password:
            errors['password'] = 'Поле обязательно для заполнения!'
        
        if errors:
            return render_template('login.html', errors=errors, email=email)  
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            errors['email'] = 'Неверный формат email! Используйте формат example@domain.com'
            return render_template('login.html', errors=errors, email=email) 
        
        user = find_user_by_email(email)
        if not user:
            errors['email'] = 'Пользователь с таким email не найден!'
            return render_template('login.html', errors=errors, email=email)  
        
        if not user.check_password(password):
            errors['password'] = 'Неверный пароль!'
            return render_template('login.html', errors=errors, email=email)  
        
        login_user(user)
        flash('Авторизация успешна!')
        return redirect(url_for('index'))
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', errors={}, name='', email='', password='')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        errors = {}
        
        if not name:
            errors['name'] = 'Поле обязательно для заполнения!'
        if not email:
            errors['email'] = 'Поле обязательно для заполнения!'
        if not password:
            errors['password'] = 'Поле обязательно для заполнения!'
        
        if errors:
            return render_template('signup.html', errors=errors, name=name, email=email, password=password)
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            errors['email'] = 'Неверный формат email! Используйте формат example@domain.com'
            return render_template('signup.html', errors=errors, name=name, email=email, password=password)
        
        if len(password) < 6:
            errors['password'] = 'Пароль должен содержать не менее 6 символов!'
            return render_template('signup.html', errors=errors, name=name, email=email, password=password)
        
        if find_user_by_email(email):
            errors['email'] = 'Пользователь с таким email уже существует!'
            return render_template('signup.html', errors=errors, name=name, email=email, password=password)
        
        new_user = User(email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Войдите в систему')
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
@login_required  
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
