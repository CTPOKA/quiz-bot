import asyncio
import logging
from database import create_table
from handlers import router
from aiogram import Bot, Dispatcher
from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
