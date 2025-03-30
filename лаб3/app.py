from flask import Flask, request, jsonify
import random
import json
import subprocess

app = Flask(__name__)

#раздел 1
#Реализовать GET эндпоинт /number/, который принимает параметр
#запроса – param с числом. Вернуть рандомно сгенерированное
#число, умноженное на значение из параметра в формате JSON
@app.route('/number', methods=['GET'])
def get_number():
    param = request.args.get('param',type=int)
    number=random.randint(0,1000)
    result=param*number
    return jsonify({'number': number,'result': result})

#Реализовать POST эндпоинт /number/, который принимает в теле
#запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно
#число, умноженное на то, что пришло в JSON и рандомно выбрать операцию.
@app.route('/number', methods=['POST'])
def post_number():
        data = request.get_json()
        json_param = data.get('jsonParam') 
        json_param = int(json_param)
        random_number = random.randint(0,1000)
        operation = random.choice(['+', '-', '*', '/'])
        if operation == '+':
            result = random_number + json_param
        elif operation == '-':
            result = random_number - json_param
        elif operation == '*':
            result = random_number * json_param
        else: 
            result = random_number / json_param
        return jsonify({'result': result, 'operation': operation})

#Реализовать DELETE эндпоинт /number/, в ответе сгенерировать
#число и рандомную операцию
@app.route('/number', methods=['DELETE'])
def delete_number():
    random_number = random.randint(0, 1000)
    operation = random.choice(['+', '-', '*', '/'])

    return jsonify({'number': random_number, 'operation': operation}), 200

def perform_api_requests():
    # Раздел II: Отправка запросов и вычисления
    # 1. GET
    param_value = random.randint(1, 10)
    get_response = app.test_client().get(f'/number?param={param_value}')
    get_data = get_response.get_json()
    get_result = get_data['result']
    print(f"GET: result={get_result}")

    # 2. POST
    json_param_value = random.randint(1, 10)
    post_response = app.test_client().post('/number', json={'jsonParam': json_param_value})
    post_data = post_response.get_json()
    post_operation = post_data['operation']
    post_result = post_data['result']
    print(f"POST: operation={post_operation}, result={post_result}")

    # 3. DELETE
    delete_response = app.test_client().delete('/number')
    delete_data = delete_response.get_json()
    delete_number = delete_data['number']
    delete_operation = delete_data['operation']
    print(f"DELETE: number={delete_number}, operation={delete_operation}")


    if post_operation == '+':
        get_result += post_result
    elif post_operation == '-':
        get_result -= post_result
    elif post_operation == '*':
        get_result *= post_result
    elif post_operation == '/':
        get_result /= post_result

    if delete_operation == '+':
        get_result += delete_number
    elif delete_operation == '-':
        get_result -= delete_number
    elif delete_operation == '*':
        get_result *= delete_number
    elif delete_operation == '/':
        get_result /= delete_number

    final_result = int(get_result)
    print(f"Конечный результат: {final_result}")

    return final_result

def perform_api_requests_with_curl():
    base_url = "http://127.0.0.1:5000/number"

    # 1. GET
    param_value = random.randint(1, 10)
    get_command = ["curl", f"{base_url}?param={param_value}"]
    get_response = subprocess.check_output(get_command).decode('utf-8')
    get_data = json.loads(get_response)
    get_result = get_data['result']
    print(f"GET: result={get_result}")

    # 2. POST
    json_param_value = random.randint(1, 10)
    post_data = {"jsonParam": json_param_value}
    post_data_string = json.dumps(post_data)

    post_command = ["curl", "-X", "POST", "-H", "Content-Type: application/json", "-d", post_data_string, base_url]

    post_response = subprocess.check_output(post_command).decode('utf-8')
    post_data = json.loads(post_response)
    post_operation = post_data.get('operation')
    post_result = post_data.get('result')
    print(f"POST: operation={post_operation}, result={post_result}")

    # 3. DELETE
    delete_command = ["curl", "-X", "DELETE", base_url]
    delete_response = subprocess.check_output(delete_command).decode('utf-8')
    delete_data = json.loads(delete_response)
    delete_number = delete_data['number']
    delete_operation = delete_data['operation']
    print(f"DELETE: number={delete_number}, operation={delete_operation}")

    intermediate_result = get_result

    if post_operation == '+':
        intermediate_result += post_result
    elif post_operation == '-':
        intermediate_result -= post_result
    elif post_operation == '*':
        intermediate_result *= post_result
    elif post_operation == '/':
        intermediate_result /= post_result

    if delete_operation == '+':
        intermediate_result += delete_number
    elif delete_operation == '-':
        intermediate_result -= delete_number
    elif delete_operation == '*':
        intermediate_result *= delete_number
    elif delete_operation == '/':
        intermediate_result /= delete_number

    final_result2 = int(intermediate_result)
    print(f"Конечный результат: {final_result2}")

if __name__ == '__main__':
    result = perform_api_requests()  
    result2=perform_api_requests_with_curl()

    
