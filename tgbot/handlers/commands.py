from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def start_command_handler(message: types.Message, state: FSMContext):
    from_user = message.from_user

    greeting_text = (
        f"С возвращением, {from_user.full_name}! Чем могу помочь?"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сохранить в БД"), KeyboardButton(text="Очистить БД")]
        ],
        resize_keyboard=True
    )

    await message.answer(greeting_text, reply_markup=keyboard)