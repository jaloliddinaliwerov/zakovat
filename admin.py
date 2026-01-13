from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMINS
from keyboards import admin_kb
from db import create_or_reset_test, set_test_active, get_rating

admin_router = Router()

def is_admin(uid): 
    return uid in ADMINS

@admin_router.message(Command("start"))
async def admin_start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👑 Admin panel", reply_markup=admin_kb)

@admin_router.message(lambda m: m.text == "➕ Test yaratish")
async def ask_create(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Format:\n/create TEST123 5")

@admin_router.message(Command("create"))
async def create_test(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 3 or not parts[2].isdigit():
        await message.answer("❌ /create TEST123 5")
        return
    await create_or_reset_test(parts[1], int(parts[2]))
    await message.answer("✅ Test yaratildi (reset qilindi)")

@admin_router.message(lambda m: m.text == "▶️ Testni ochish")
async def open_info(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Format:\n/start_test TEST123")

@admin_router.message(Command("start_test"))
async def start_test(message: Message):
    parts = message.text.split()
    if len(parts) == 2:
        await set_test_active(parts[1], 1)
        await message.answer("✅ Test ochildi")

@admin_router.message(lambda m: m.text == "⛔ Testni yopish")
async def close_info(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Format:\n/finish_test TEST123")

@admin_router.message(Command("finish_test"))
async def finish_test(message: Message):
    parts = message.text.split()
    if len(parts) == 2:
        await set_test_active(parts[1], 0)
        await message.answer("⛔ Test yopildi")

@admin_router.message(lambda m: m.text == "📊 Reyting")
async def rating(message: Message):
    rows = await get_rating("TEST123")
    if not rows:
        await message.answer("❌ Reyting yo‘q")
        return

    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>TOP-10 REYTING</b>\n\n"
    for i, (team, score) in enumerate(rows):
        place = medals[i] if i < 3 else f"{i+1}."
        text += f"{place} <b>{team}</b> — {score} ball\n"

    await message.answer(text, parse_mode="HTML")
