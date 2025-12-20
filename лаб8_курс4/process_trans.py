import asyncio
import json
from collections import defaultdict

async def load_transactions(filename="transactions.json"):
    """Асинхронно загружает транзакции из JSON-файла."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
   

async def process_transactions(transactions):
    """Обрабатывает транзакции: группировка по категориям, суммирование amount, проверка превышений."""
    category_sums = defaultdict(float)
    
    for transaction in transactions:
        category = transaction.get("category")
        amount = transaction.get("amount", 0)
        if category:
            category_sums[category] += amount
    
    # Вывод результатов
    for category, total in category_sums.items():
        print(f"Категория '{category}': общая сумма {total:.2f} рублей")
        if total > 10000:
            print(f"  ВНИМАНИЕ: Превышение расходов в категории '{category}' (более 10000 рублей)!")

async def main():
    transactions = await load_transactions()
    if not transactions:
        return
    
    await process_transactions(transactions)
    print("Обработка завершена.")

if __name__ == "__main__":
    asyncio.run(main())
