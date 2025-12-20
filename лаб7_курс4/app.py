from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)

# Инициализация лимитера 
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"]  # Общее ограничение для всех маршрутов: 100 запросов в сутки
)

# Глобальный словарь для хранения данных
data = {}

# Функция для загрузки данных из файла при старте
def load_data():
    global data
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)
    else:
        data = {}

# Функция для сохранения данных в файл
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Загружаем данные при старте приложения
load_data()

#сохранить ключ-значение
@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")  # ограничение: 10 запросов в минуту
def set_value():
    req_data = request.get_json() # Извлекаем JSON-данные из тела POST-запроса
    key = req_data['key']
    value = req_data['value']
    data[key] = value
    save_data()  # Сохраняем изменения
    return jsonify({"message": f"Ключ '{key}' установлен на '{value}'"}), 200


@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    return jsonify({"ключ": key, "значение": data[key]}), 200


@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")  # ограничение: 10 запросов в минуту
def delete_value(key):
    del data[key]
    save_data()  # Сохраняем изменения
    return jsonify({"message": f"КЛюч '{key}' удален"}), 200

# проверить наличие ключа
@app.route('/exists/<key>', methods=['GET'])
def exists_key(key):
    exists = key in data
    return jsonify({"key": key, "exists": exists}), 200

if __name__ == '__main__':
    app.run(debug=True)
