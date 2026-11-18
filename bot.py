import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ---
BOT_TOKEN = "ВАШ_ТОКЕН_СЮДА"   # Вставьте токен от BotFather (в кавычках!)
ADMIN_ID = 8553406744           # Вставьте ваш ID от @userinfobot (БЕЗ кавычек!)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    phone = State()
    interest = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Это бот для сбора заявок.\n"
        "Давайте оформим вашу заявку. Как вас зовут?"
    )
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь напишите ваш номер телефона.")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if sum(c.isdigit() for c in phone) < 5:
        await message.answer("Пожалуйста, введите номер телефона (хотя бы 5 цифр).")
        return
    await state.update_data(phone=phone)
    await message.answer("Что вас интересует? Кратко опишите.")
    await state.set_state(Form.interest)

@dp.message(Form.interest)
async def process_interest(message: types.Message, state: FSMContext):
    await state.update_data(interest=message.text)
    data = await state.get_data()

    text_to_admin = (
        f"📩 Новая заявка!\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Интерес: {data['interest']}\n"
        f"От: @{message.from_user.username or message.from_user.id}"
    )
    await bot.send_message(ADMIN_ID, text_to_admin)

    await message.answer(
        "Спасибо! Ваша заявка принята. Мы свяжемся с вами."
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())