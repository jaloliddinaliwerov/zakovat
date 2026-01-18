import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from admin import admin_router
from user import user_router

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())  # 🔴 MUHIM

    dp.include_router(admin_router)
    dp.include_router(user_router)

    print("BOT ISHGA TUSHDI")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
