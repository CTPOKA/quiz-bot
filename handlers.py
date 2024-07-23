from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import quiz_data
from service import quiz_data, generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, get_score, update_score, get_statistics

router = Router()

main_menu = types.ReplyKeyboardMarkup(
    keyboard=[[
        types.KeyboardButton(text="Начать игру"),
        types.KeyboardButton(text="Статистика")
    ]],
    resize_keyboard=True
)

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    current_score = await get_score(callback.from_user.id)
    current_score += 1
    await update_score(callback.from_user.id, current_score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {current_score}/{len(quiz_data)}", reply_markup=main_menu)

  
@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        current_score = await get_score(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {current_score}/{len(quiz_data)}", reply_markup=main_menu)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    
    url = "https://storage.yandexcloud.net/bucket-z0001/quiz_bot_icon.png"
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=url,
        caption="Добро пожаловать в квиз!"
    )


@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


@router.message(F.text == "Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):

    stats = await get_statistics()
    if stats:
        stats_message = "Статистика игроков:\n\n"
        for row in stats:
            stats_message += f"User ID: {row.user_id} - Правильных ответов: {row.score}\n"
    else:
        stats_message = "Статистика пуста."
    await message.answer(stats_message)