from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()





async def get_question(message, user_id):
    
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    current_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_score(user_id, current_score)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    

    
    

async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )
    


async def get_score(user_id):
    get_user_score = f"""
        DECLARE $user_id AS Uint64;

        SELECT score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_score, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["score"] is None:
        return 0
    return results[0]["score"]    


async def update_score(user_id, score):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $score AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `score`)
        VALUES ($user_id, $score);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        score=score,
    )



async def get_statistics():
    get_quiz_state = f"""
        SELECT user_id, score
        FROM `quiz_state`
    """
    results = execute_select_query(pool, get_quiz_state)

    if len(results) == 0:
        return 0
    return results