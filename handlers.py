from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F, Router

from utils import generate_options_keyboard
from database import (get_quiz_index, update_quiz_index, get_correct_answers, update_correct_answers, get_statistics)
from questions import quiz_data

router = Router()

main_menu = types.ReplyKeyboardMarkup(
    keyboard=[[
        types.KeyboardButton(text="Начать игру"),
        types.KeyboardButton(text="Статистика")
    ]],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=main_menu)

@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await update_correct_answers(message.from_user.id, 0)
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

@router.message(F.text == "Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    stats = await get_statistics()
    if stats:
        stats_message = "Статистика игроков:\n\n"
        for user_id, correct_answers in stats:
            stats_message += f"User ID: {user_id} - Правильных ответов: {correct_answers}\n"
    else:
        stats_message = "Статистика пуста."
    await message.answer(stats_message)

@router.callback_query()
async def quiz_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option_index = quiz_data[current_question_index]['correct_option']
    correct_option = quiz_data[current_question_index]['options'][correct_option_index]
    user_answer_index = int(callback.data)
    user_answer = quiz_data[current_question_index]['options'][user_answer_index]
    correct_answers = await get_correct_answers(callback.from_user.id)
    
    if user_answer_index == correct_option_index:
        answer_text = "Верно!"
        correct_answers += 1
        await update_correct_answers(callback.from_user.id, correct_answers)
    else:
        answer_text = f"Неправильно.\nПравильный ответ: {correct_option}."
    answer_text += f"\nВаш ответ: {user_answer}."
    await callback.message.answer(answer_text)
    
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Начать игру"))
        builder.add(types.KeyboardButton(text="Статистика"))
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {correct_answers}/{len(quiz_data)}", reply_markup=main_menu)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)
