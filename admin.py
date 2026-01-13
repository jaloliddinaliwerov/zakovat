from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMINS
from db import create_test, set_test_active, add_question

admin_router = Router()

def is_admin(uid):
    return uid in ADMINS


@admin_router.message(Command("start"))
async def admin_start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer(
            "👑 ADMIN PANEL\n\n"
            "/create TEST123\n"
            "/add_question TEST123 1 A\n"
            "/start_test TEST123\n"
            "/stop_test TEST123"
        )


@admin_router.message(Command("create"))
async def create(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("/create TEST123")
        return

    await create_test(parts[1])
    await message.answer("✅ Test yaratildi")


@admin_router.message(Command("add_question"))
async def add_q(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) != 4 or not parts[2].isdigit():
        await message.answer("/add_question TEST123 1 A")
        return

    await add_question(parts[1], int(parts[2]), parts[3])
    await message.answer("✅ Savol va javob qo‘shildi")


@admin_router.message(Command("start_test"))
async def start_test(message: Message):
    parts = message.text.split()
    if len(parts) == 2:
        await set_test_active(parts[1], 1)
        await message.answer("▶️ Test ochildi")


@admin_router.message(Command("stop_test"))
async def stop_test(message: Message):
    parts = message.text.split()
    if len(parts) == 2:
        await set_test_active(parts[1], 0)
        await message.answer("⛔ Test yopildi")
