from aiogram import Router, F
from aiogram.types import Message
from config import ADMIN_IDS
from keyboards import admin_keyboard
from db import create_test

admin_router = Router()

@admin_router.message(F.from_user.id.in_(ADMIN_IDS), F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer(
        "👑 Admin panel",
        reply_markup=admin_keyboard()
    )

@admin_router.message(F.from_user.id.in_(ADMIN_IDS), F.text == "➕ Test yaratish")
async def create_test_start(message: Message):
    await message.answer(
        "Test kodini va savollar sonini yubor:\n\nMasalan:\nTEST123 5"
    )

@admin_router.message(F.from_user.id.in_(ADMIN_IDS))
async def create_test_process(message: Message):
    try:
        code, count = message.text.split()
        create_test(code, int(count))
        await message.answer("✅ Test yaratildi")
    except:
        await message.answer("❌ Noto‘g‘ri format")
