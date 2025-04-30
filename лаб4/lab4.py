import os, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext  
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

currency_rates = {}

class Form(StatesGroup):
    save_currency_name = State()
    save_currency_rate = State()
    convert_currency_name = State()
    convert_amount = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Приветствую! Я бот-конвертер валют, к вашим услугам!\n"
                        "Устал считать в уме? Я помогу! 💸\n"
                        "Мои команды:\n"
                        "/save_currency - Чтобы сохранить курс, как настоящий финансист.\n"
                        "/convert - Чтобы получить рубли, как бизнесмен!")


@dp.message(Command("save_currency"))
async def save_currency_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.save_currency_name)
    await message.answer("Введите название валюты (например, USD, EUR):")


@dp.message(Form.save_currency_name)
async def get_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency=currency_name)
    await state.set_state(Form.save_currency_rate)
    await message.answer(f"Введите курс {currency_name} к рублю:")


@dp.message(Form.save_currency_rate)
async def get_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return
    data = await state.get_data()
    currency_name = data["currency"]
    currency_rates[currency_name] = rate
    await state.clear()
    await message.answer(f"Курс {currency_name} к рублю сохранен.")


@dp.message(Command("convert"))
async def convert_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.convert_currency_name)
    await message.answer("Введите название валюты, которую хотите конвертировать в рубли:")


@dp.message(Form.convert_currency_name)
async def get_currency_to_convert(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency=currency_name)
    await state.set_state(Form.convert_amount)
    await message.answer(f"Введите сумму в {currency_name} для конвертации:")


@dp.message(Form.convert_amount)
async def get_amount_to_convert(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return
    data = await state.get_data()
    currency_name = data["currency"]

    if currency_name not in currency_rates:
        await message.answer(f"Курс для валюты {currency_name} не найден. Пожалуйста, сначала сохраните курс с помощью команды /save_currency.")
        await state.clear()
        return
    rate = currency_rates[currency_name]
    rubles = amount * rate
    await state.clear()
    await message.answer(f"{amount} {currency_name} = {rubles:.2f} RUB")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())