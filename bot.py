import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
ADMIN_ID = 8553406744

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    phone = State()
    interest = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Это бот для сбора заявок.\nДавайте оформим вашу заявку. Как вас зовут?")
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
    await message.answer("Спасибо! Ваша заявка принята. Мы свяжемся с вами.")
    await state.clear()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не засыпал) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    # Запускаем веб-сервер и бота одновременно
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
