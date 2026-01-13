from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMINS
from states import AdminState
from db import create_test, open_test, add_question
from keyboards import admin_kb

admin_router = Router()

@admin_router.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id in ADMINS:
        await msg.answer("👑 Admin panel", reply_markup=admin_kb)

@admin_router.callback_query(F.data == "create_test")
async def ct(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Test kodini yubor:")
    await state.set_state(AdminState.create_test)

@admin_router.message(AdminState.create_test)
async def ct2(msg: Message, state: FSMContext):
    await create_test(msg.text)
    await msg.answer("✅ Test yaratildi")
    await state.clear()

@admin_router.callback_query(F.data == "add_q")
async def aq(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Format:\nTEST123 1 A")
    await state.set_state(AdminState.add_question)

@admin_router.message(AdminState.add_question)
async def aq2(msg: Message, state: FSMContext):
    code, q, ans = msg.text.split()
    await add_question(code, int(q), ans)
    await msg.answer("✅ Savol qo‘shildi")
    await state.clear()

@admin_router.callback_query(F.data == "open")
async def ot(cb: CallbackQuery):
    await open_test(cb.message.text, 1)
    await cb.message.answer("▶️ Test ochildi")

@admin_router.callback_query(F.data == "close")
async def ct(cb: CallbackQuery):
    await open_test(cb.message.text, 0)
    await cb.message.answer("⛔ Test yopildi")
