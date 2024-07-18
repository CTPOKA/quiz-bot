from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=str(index))
        )
    builder.adjust(1)
    return builder.as_markup()
