from flask import Flask, jsonify
import sys

app = Flask(__name__)

# Уникальный ID инстанса на основе порта
if len(sys.argv) > 1: # проверка сколько аргументов передано
    port = int(sys.argv[1]) # берет второй элемент из sys.argv
    instance_id = f"instance_{port}" # создание id для порта
else:
    port = 5001
    instance_id = "instance_5001"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "instance_id": instance_id})

@app.route('/process', methods=['GET'])
def process():
    return jsonify({"instance_id": instance_id, "message": "Processed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
