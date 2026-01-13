from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def sub_kb(channels):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ch, url=f"https://t.me/{ch[1:]}")]
        for ch in channels
    ] + [[InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]])


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Test yaratish")],
        [KeyboardButton(text="➕ Savol qo‘shish")],
        [KeyboardButton(text="▶️ Testni ochish")],
        [KeyboardButton(text="⛔ Testni yopish")],
        [KeyboardButton(text="📊 Statistika")],
    ],
    resize_keyboard=True
)
