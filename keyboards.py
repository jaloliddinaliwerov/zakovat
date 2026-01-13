from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def sub_kb(channels):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ch, url=f"https://t.me/{ch[1:]}")]
        for ch in channels
    ] + [[InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Test yaratish", callback_data="create_test")],
    [InlineKeyboardButton(text="➕ Savol qo‘shish", callback_data="add_q")],
    [InlineKeyboardButton(text="▶️ Testni ochish", callback_data="open")],
    [InlineKeyboardButton(text="⛔ Testni yopish", callback_data="close")],
])
