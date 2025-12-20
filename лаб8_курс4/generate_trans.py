import asyncio
import json
import random
import sys
from datetime import datetime

# Определяем категории транзакций
CATEGORIES = ["развлечения", "покупки", "здоровье", "быт"]

def generate_transaction():
    """Генерирует одну транзакцию."""
    return {
        "timestamp": datetime.now().isoformat(),
        "category": random.choice(CATEGORIES),
        "amount": random.randint(100, 5000)
    }

async def save_batch_to_file(batch, filename):
    """Асинхронно сохраняет список транзакций в JSON-файл."""
    try:
        # Читаем существующий файл, если он есть
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        
        # Добавляем новый батч
        data.extend(batch)
        
        # Сохраняем обратно
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Сохранен батч из {len(batch)} транзакций. Общее количество: {len(data)}")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

async def generate_and_save(num_transactions, filename="transactions.json"):
    """Основная функция для генерации и сохранения транзакций."""
    batch_size = 10
    batch = []
    
    for i in range(num_transactions):
        transaction = generate_transaction() 
        batch.append(transaction)
        
        if len(batch) == batch_size or i == num_transactions - 1:
            await save_batch_to_file(batch, filename)
            batch = []
    
    print(f"Генерация завершена. Всего транзакций: {num_transactions}")

async def main():
    if len(sys.argv) != 2:
        print("Использование: python generate_transactions.py <количество_транзакций>")
        return
    
    num_transactions = int(sys.argv[1])
    if num_transactions <= 0:
        print("Пожалуйста, укажите положительное целое число.")
        return
    
    await generate_and_save(num_transactions)

if __name__ == "__main__":
    asyncio.run(main())
