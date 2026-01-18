from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Test yaratish")]
        ],
        resize_keyboard=True
    )

def remove_keyboard():
    return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
