from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import CHANNELS

# Admin panel
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Test yaratish")],
        [KeyboardButton(text="▶️ Testni ochish"), KeyboardButton(text="⛔ Testni yopish")],
        [KeyboardButton(text="📊 Reyting")]
    ],
    resize_keyboard=True
)

# Majburiy azolik
def subscribe_kb():
    buttons = []
    for ch in CHANNELS:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {ch}",
                url=f"https://t.me/{ch.replace('@','')}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
