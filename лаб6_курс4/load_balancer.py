from flask import Flask, request, jsonify, redirect, url_for, render_template_string
import requests
import threading
import time

app = Flask(__name__)

# Список инстансов: [{"ip": "127.0.0.1", "port": 5001, "healthy": True}, ...]
instances = []
current_index = 0  # счетчик для алгоритма Round Robin

# HTML-шаблон для Web UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Load Balancer Management</title></head>
<body>
    <h1>Управление пулом инстансов</h1>
    <form action="/add_instance" method="post">
        IP: <input type="text" name="ip" value="127.0.0.1"><br>
        Port: <input type="number" name="port"><br>
        <button type="submit">Добавить инстанс</button>
    </form>
    <h2>Текущие инстансы</h2>
    <ul>
        {% for idx, inst in enumerate(instances) %}
        <li>{{ inst['ip'] }}:{{ inst['port'] }} - {{ 'Доступен' if inst['healthy'] else 'Недоступен' }}
            <form action="/remove_instance" method="post" style="display:inline;">
                <input type="hidden" name="index" value="{{ idx }}">
                <button type="submit">Удалить</button>
            </form>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
"""
#проверка состояния инстанса каждые 5 сек
def check_health():
    while True:
        for inst in instances:
            response = requests.get(f"http://{inst['ip']}:{inst['port']}/health", timeout=2)
            inst['healthy'] = response.status_code == 200
        time.sleep(5)

# Запуск проверки состояния в фоне
threading.Thread(target=check_health, daemon=True).start() # daemon - поток завершится при остановке основного приложения

@app.route('/health', methods=['GET'])
def health():
    # Возвращает статус всех инстансов
    return jsonify([{"ip": i['ip'], "port": i['port'], "healthy": i['healthy']} for i in instances])

@app.route('/process', methods=['GET'])
def process():
    # Перенаправление на следующий здоровый инстанс по Round Robin
    global current_index
    # Фильтрует только здоровые инстансы
    healthy_instances = [i for i in instances if i['healthy']]
    if not healthy_instances:
        return jsonify({"error": "Нет здоровых инстансов"}), 503
    instance = healthy_instances[current_index % len(healthy_instances)]
    current_index += 1
    #Запрос на выбранный инстанс
    response = requests.get(f"http://{instance['ip']}:{instance['port']}/process")
    return response.json()

# рендерит HTML-шаблон с текущим списком инстансов
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, instances=instances, enumerate=enumerate)


@app.route('/add_instance', methods=['POST'])
def add_instance():
    ip = request.form.get('ip')
    port = int(request.form.get('port'))
    if not any(i['ip'] == ip and i['port'] == port for i in instances):
        instances.append({"ip": ip, "port": port, "healthy": False})
    return redirect(url_for('index'))

# Удаляет инстанс по индексу из формы
@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index = int(request.form.get('index'))
    if 0 <= index < len(instances):
        instances.pop(index)
    return redirect(url_for('index'))

# перехватывает запросы и перенаправляет их
# на доступные инстансы с использованием стратегии Round Robin
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Перенаправление всех остальных запросов по Round Robin
    global current_index
    healthy_instances = [i for i in instances if i['healthy']]
    if not healthy_instances:
        return jsonify({"error": "Нет здоровых истансов"}), 503
    instance = healthy_instances[current_index % len(healthy_instances)]
    current_index += 1

    url = f"http://{instance['ip']}:{instance['port']}/{path}"
    response = requests.request(request.method, url, data=request.data, headers=request.headers)
    return response.content, response.status_code


if __name__ == '__main__':
    app.run(port=5000, debug=True)
