import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db import init_db
from admin import admin_router
from user import user_router

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
