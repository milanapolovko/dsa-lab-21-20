import os
import asyncio
import psycopg2
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    manage_action = State()  
    currency_name = State()  
    rate = State() 
    convert_currency_name = State()
    convert_amount = State()

def db_connect():
    conn= psycopg2.connect(
        host="127.0.0.1",
        database="milana_polovko",
        user="milana_polovko",
        password="rfifvfkfif44"
    )
    cur=conn.cursor()

    return conn,cur

conn, cur = db_connect()

cur.execute(
    "CREATE TABLE IF NOT EXISTS currencies("
    "id SERIAL PRIMARY KEY,"
    "currency_name VARCHAR UNIQUE NOT NULL,"
    "rate NUMERIC NOT NULL)"
)
conn.commit()

cur.execute(
    "CREATE TABLE IF NOT EXISTS admins("
    "id SERIAL PRIMARY KEY,"
    "chat_id VARCHAR UNIQUE NOT NULL)"
)
conn.commit()  
conn.close()


def is_admin(chat_id):
    conn, cur = db_connect()
    cur.execute("SELECT * FROM admins WHERE chat_id =%s", (str(chat_id),))
    admin = cur.fetchone()
    cur.close()
    conn.close()
    return admin 


def get_currency_rate_from_db(currency_name):
    conn, cur = db_connect()
    if conn:
            cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))  
            result = cur.fetchone()
            if result:
                return float(result[0]) 
            return None  
   
    
def get_all_currencies_from_db():
    conn, cur = db_connect()
    if conn:      
        cur.execute("SELECT currency_name, rate FROM currencies")
        currencies = cur.fetchall()
        cur.close()
        conn.close()
        return currencies


@dp.message(Command("start"))
async def start(message: types.Message):

    if is_admin(message.chat.id):
        keyboard = InlineKeyboardMarkup( inline_keyboard=[
            [
            InlineKeyboardButton(text="Управление валютами", callback_data="manage_currencies"),
            InlineKeyboardButton(text="Список валют", callback_data="get_currencies"),
            InlineKeyboardButton(text="Конвертировать", callback_data="convert_currency"),
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
            InlineKeyboardButton(text="Список валют", callback_data="get_currencies"),
            InlineKeyboardButton(text="Конвертировать", callback_data="convert_currency"),
            ]
        ])
    
    await message.answer("Приветствую! Я бот-конвертер валют, к вашим услугам!\n"
                        "Устал считать в уме? Я помогу! 💸\n",
                        reply_markup=keyboard)


@dp.callback_query(F.data == "manage_currencies")
async def manage_currencies(callback_query: types.CallbackQuery):
 
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Нет доступа к команде.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить валюту", callback_data="add_currency"),
            InlineKeyboardButton(text="Удалить валюту", callback_data="delete_currency"),
            InlineKeyboardButton(text="Изменить курс валюты", callback_data="update_currency")
        ]
    ])
    
    await callback_query.message.answer("Выберите действие:", reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)  


@dp.callback_query(F.data.in_({"add_currency", "delete_currency", "update_currency"}))
async def manage_currency_callback(callback_query: types.CallbackQuery, state: FSMContext):
   
    manage_action = callback_query.data  
    await state.set_state(Form.manage_action) 
    await state.update_data(manage_action=manage_action)  
    await bot.answer_callback_query(callback_query.id)

    if manage_action == "add_currency" or manage_action == "delete_currency" or manage_action == "update_currency":
        await bot.send_message(callback_query.from_user.id, "Введите название валюты:")  
        await state.set_state(Form.currency_name)   


@dp.message(Form.currency_name)
async def manage_currency_name(message: types.Message, state: FSMContext):
  
    currency_name = message.text.upper()  
    data = await state.get_data() 
    manage_action = data.get("manage_action")

    conn, cur = db_connect()
    if conn:
        if manage_action == "add_currency":
        
            cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
            if cur.fetchone() is not None:
                await message.answer("Данная валюта уже существует.")  
                await state.clear()
                return
            
            await state.update_data(currency_name=currency_name)  
            await message.answer("Введите курс к рублю:") 
            await state.set_state(Form.rate)

        elif manage_action == "delete_currency" or manage_action == "update_currency":
        
            cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
            if cur.fetchone() is None:
                await message.answer("Данная валюта не существует.")  
                await state.clear()
                return
            
            await state.update_data(currency_name=currency_name)  
            
            if manage_action == "delete_currency":
                cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
                conn.commit()  
                await message.answer(f"Валюта {currency_name} успешно удалена.")
                await state.clear() 
                
            elif manage_action == "update_currency":
                await message.answer("Введите курс к рублю:") 
                await state.set_state(Form.rate) 
    
    cur.close()
    conn.close()


@dp.message(Form.rate)
async def manage_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")  
        return

    data = await state.get_data()  
    currency_name = data["currency_name"]  
    manage_action = data["manage_action"] 

    conn, cur = db_connect()

    if manage_action == "add_currency":
        cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s,%s)", (currency_name, rate))
        await message.answer(f"Валюта: {currency_name} успешно добавлена.")
    
    elif manage_action == "update_currency":
        cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, currency_name))
        await message.answer(f"Курс валюты {currency_name} успешно изменен.") 

    conn.commit()  
    conn.close()
    await state.clear()  


@dp.callback_query(F.data =="get_currencies")
async def get_currencies(callback_query: types.CallbackQuery):
    
    currencies = get_all_currencies_from_db()  
 
    if not currencies:
        await bot.send_message(callback_query.from_user.id, "Нет сохраненных валют.")
        await bot.answer_callback_query(callback_query.id)
        return 

    response = "Курсы валют:\n"
    for currency_name, rate in currencies:
        response += f"{currency_name}: {rate}\n"  

    await bot.send_message(callback_query.from_user.id, response)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query(F.data =="convert_currency")
async def get_currencies(callback_query: types.CallbackQuery, state: FSMContext):
    
    await state.set_state(Form.convert_currency_name)  
    await callback_query.message.answer("Введите название валюты:") 
    await bot.answer_callback_query(callback_query.id)


@dp.message(Form.convert_currency_name)
async def get_currency_to_convert(message: types.Message, state: FSMContext):

    currency_name = message.text.upper()  
    rate = get_currency_rate_from_db(currency_name) 
    await state.update_data(currency_name=currency_name, rate=rate) 
    await state.set_state(Form.convert_amount)  
    await message.answer("Введите сумму:")  


@dp.message(Form.convert_amount)
async def get_amount_to_convert(message: types.Message, state: FSMContext):
  
    try:
        amount = float(message.text) 
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.") 
        return

    data = await state.get_data()
    currency_name = data["currency_name"] 
    rate = data["rate"]  
    if rate is None:
        await message.answer("Курс для данной валюты не найден. Пожалуйста, начните конвертацию заново.")
        await state.clear()
        return
    rubles = amount*rate 
    await state.clear()  
    await message.answer(f"{amount} {currency_name} = {rubles:.2f} RUB") 


async def main():
    await dp.start_polling(bot) 

if __name__ == '__main__':
    asyncio.run(main())  