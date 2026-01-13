from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMINS
from states import AdminState
from db import create_test, open_test, add_question
from keyboards import admin_kb

admin_router = Router()


# ===============================
# ADMIN PANELNI OCHISH
# ===============================
@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer("👑 Admin panel", reply_markup=admin_kb)


# ===============================
# TEST YARATISH
# ===============================
@admin_router.callback_query(F.data == "create_test")
async def create_test_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in ADMINS:
        return
    await cb.message.answer("🧪 Test kodini yuboring:")
    await state.set_state(AdminState.create_test)
    await cb.answer()


@admin_router.message(AdminState.create_test)
async def create_test_finish(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    test_code = message.text.strip()
    await create_test(test_code)

    await message.answer(f"✅ Test yaratildi:\n<code>{test_code}</code>")
    await state.clear()


# ===============================
# SAVOL + JAVOB QO‘SHISH
# ===============================
@admin_router.callback_query(F.data == "add_q")
async def add_question_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in ADMINS:
        return
    await cb.message.answer(
        "➕ Savol qo‘shish formati:\n"
        "<code>TEST123 1 A</code>\n\n"
        "Ya'ni: test_kodi savol_raqami to‘g‘ri_javob"
    )
    await state.set_state(AdminState.add_question)
    await cb.answer()


@admin_router.message(AdminState.add_question)
async def add_question_finish(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.answer("❌ Format noto‘g‘ri. Qayta yuboring.")
        return

    test_code, q_num, correct = parts

    if not q_num.isdigit():
        await message.answer("❌ Savol raqami son bo‘lishi kerak.")
        return

    await add_question(
        test_code=test_code,
        q=int(q_num),
        correct=correct.strip()
    )

    await message.answer(
        f"✅ Savol qo‘shildi\n"
        f"Test: <code>{test_code}</code>\n"
        f"Savol: <b>{q_num}</b>\n"
        f"Javob: <b>{correct}</b>"
    )
    await state.clear()


# ===============================
# TESTNI OCHISH
# ===============================
@admin_router.callback_query(F.data == "open")
async def open_test_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in ADMINS:
        return
    await cb.message.answer("▶️ Qaysi testni OCHAMIZ? Test kodini yuboring:")
    await state.set_state(AdminState.create_test)
    await cb.answer()


@admin_router.message(AdminState.create_test)
async def open_test_finish(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    test_code = message.text.strip()
    await open_test(test_code, 1)

    await message.answer(f"▶️ Test ochildi:\n<code>{test_code}</code>")
    await state.clear()


# ===============================
# TESTNI YOPISH
# ===============================
@admin_router.callback_query(F.data == "close")
async def close_test_start(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id not in ADMINS:
        return
    await cb.message.answer("⛔ Qaysi testni YOPAMIZ? Test kodini yuboring:")
    await state.set_state(AdminState.create_test)
    await cb.answer()


@admin_router.message(AdminState.create_test)
async def close_test_finish(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    test_code = message.text.strip()
    await open_test(test_code, 0)

    await message.answer(f"⛔ Test yopildi:\n<code>{test_code}</code>")
    await state.clear()
