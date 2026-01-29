import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ← ТВОИ ДАННЫЕ ЗДЕСЬ
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ← ТВОИ ДАННЫЕ ЗДЕСЬ
API_TOKEN = "8425957813:AAG95wj5R6MCe7HqX7QcAXetcpzS1rWoNns"  # Твой токен в кавычках!
ADMIN_CHAT_ID = 1659160019 # Твой chat ID БЕЗ кавычек!

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ← ИСПРАВЛЕНО!
)
dp = Dispatcher()


# Машина состояний для заявки
class OrderForm(StatesGroup):
    name = State()
    phone = State()
    comment = State()










#hhhhhh


# Клавиатура
def main_kb():
    kb = [[KeyboardButton(text="Оформить заказ")]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для приёма заказов.\nНажми кнопку ниже, чтобы оформить заявку.",
        reply_markup=main_kb()
    )


@dp.message(F.text == "Оформить заказ")
async def order_start(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(OrderForm.name)


@dp.message(OrderForm.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(OrderForm.phone)


@dp.message(OrderForm.phone)
async def order_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Опишите ваш заказ или оставьте комментарий:")
    await state.set_state(OrderForm.comment)


@dp.message(OrderForm.comment)
async def order_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "<b>Новая заявка</b>\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Комментарий: {data['comment']}\n"
        f"Telegram: @{message.from_user.username or 'нет юзернейма'}\n"
        f"ID: {message.from_user.id}"
    )

    # Отправляем вам
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)

    # Подтверждение пользователю
    await message.answer("Спасибо! Заявка отправлена, мы свяжемся с вами в ближайшее время.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ← ИСПРАВЛЕНО!
)
dp = Dispatcher()


# Машина состояний для заявки
class OrderForm(StatesGroup):
    name = State()
    phone = State()
    comment = State()


# Клавиатура
def main_kb():
    kb = [[KeyboardButton(text="Оформить заказ")]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для приёма заказов.\nНажми кнопку ниже, чтобы оформить заявку.",
        reply_markup=main_kb()
    )


@dp.message(F.text == "Оформить заказ")
async def order_start(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(OrderForm.name)


@dp.message(OrderForm.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(OrderForm.phone)


@dp.message(OrderForm.phone)
async def order_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Опишите ваш заказ или оставьте комментарий:")
    await state.set_state(OrderForm.comment)


@dp.message(OrderForm.comment)
async def order_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    await state.clear()

    text = (
        "<b>Новая заявка</b>\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Комментарий: {data['comment']}\n"
        f"Telegram: @{message.from_user.username or 'нет юзернейма'}\n"
        f"ID: {message.from_user.id}"
    )

    # Отправляем вам
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)

    # Подтверждение пользователю
    await message.answer("Спасибо! Заявка отправлена, мы свяжемся с вами в ближайшее время.")


async def main(): #333
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    # 111
