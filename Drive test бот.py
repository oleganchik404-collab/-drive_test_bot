import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ====== Налаштування ======
BOT_TOKEN = "7865359149:AAERvVmd4q8UN-JFNg3wfgiQAtt5fXKhLA8"
GROUP_ID = -1003507718905  # встав ID вашої групи

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ====== Стани бота ======
class Booking(StatesGroup):
    service = State()
    car = State()
    preferred_time = State()
    phone = State()

# Послуги СТО
services = ["Заміна масла 🛢️", "Діагностика 🔧", "Ремонт ходової 🚗"]

# Тимчасове зберігання даних клієнта
user_data = {}

# ====== Старт ======
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Записатися")]],
        resize_keyboard=True
    )
    await message.answer(
        "🌟 Привіт! Ласкаво просимо до *Drive Test* – тут твоє авто в надійних руках 🚗💛\n\n"
        "Ми не просто робимо ремонт – ми дбаємо, щоб твій автомобіль працював як новий 🔧\n"
        "Тисни кнопку 'Записатися' ⬇️ і давай домовимось про твоє авто 😎",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await state.clear()

# ====== Всі кроки ======
@dp.message()
async def all_steps(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    data = user_data.get(chat_id, {})

    # 1. Кнопка "Записатися" -> вибір послуги
    if not data.get("service"):
        if message.text == "Записатися":
            kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=s)] for s in services],
                resize_keyboard=True
            )
            await message.answer("🛠️ Обери послугу, яку хочеш замовити:", reply_markup=kb)
        elif message.text in services:
            data["service"] = message.text
            await message.answer("🚗 Розкажи трохи про авто – марка, модель, рік (в одному повідомленні):")
        else:
            await message.answer("Натисни 'Записатися' або обери послугу з кнопок 😎")
        user_data[chat_id] = data
        return

    # 2. Авто
    if not data.get("car"):
        data["car"] = message.text
        await message.answer("⏰ Коли тобі зручно приїхати? Напиши дату і приблизний час:")
        user_data[chat_id] = data
        return

    # 3. Зручний час
    if not data.get("preferred_time"):
        data["preferred_time"] = message.text
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Надати номер телефону 📞", request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer("Щоб ми могли зв’язатися з тобою, залиш номер телефону:", reply_markup=kb)
        user_data[chat_id] = data
        return

    # 4. Телефон
    if not data.get("phone"):
        if message.contact:
            data["phone"] = message.contact.phone_number
        else:
            data["phone"] = message.text

        # Пересилаємо в групу
        msg_text = (
            f"🔔 *Нова заявка від клієнта!* 🔔\n\n"
            f"🛠 Послуга: {data['service']}\n"
            f"🚗 Авто: {data['car']}\n"
            f"⏰ Клієнт написав зручний час: {data['preferred_time']}\n"
            f"📞 Телефон: {data['phone']}\n\n"
            f"➡️ [Натисни тут, щоб написати клієнту](tg://user?id={chat_id})"
        )
        await bot.send_message(GROUP_ID, msg_text, parse_mode="Markdown")
        await message.answer("✅ Дякуємо! Ми отримали твоє замовлення 😎\nМенеджер зв'яжеться найближчим часом 📲")
        user_data.pop(chat_id)
        return

# ====== Запуск бота ======
async def main():
    print("Drive Test Bot запущений! 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
