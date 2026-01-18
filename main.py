import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from admin import admin_router
from user import user_router

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(user_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
