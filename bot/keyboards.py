from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.enums import ButtonTexts, CallbackData

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonTexts.PARSE_REVIEWS)],
            [KeyboardButton(text=ButtonTexts.SETTINGS)]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_settings_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonTexts.LINKS)],
            [KeyboardButton(text=ButtonTexts.MAIN_MENU)]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_links_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonTexts.ADD_LINK)],
            [KeyboardButton(text=ButtonTexts.DELETE_LINK)],
            [KeyboardButton(text=ButtonTexts.SHOW_ALL_LINKS)],
            [KeyboardButton(text=ButtonTexts.BACK)]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_back_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonTexts.BACK)]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_add_links_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💾 Сохранить", callback_data=CallbackData.SAVE_LINKS),
                InlineKeyboardButton(text="➕ Добавить ссылку", callback_data=CallbackData.ADD_MORE_LINKS)
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=CallbackData.CANCEL_LINKS)]
        ]
    )
    return keyboard

def get_delete_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data=CallbackData.CONFIRM_DELETE),
                InlineKeyboardButton(text="❌ Отмена", callback_data=CallbackData.CANCEL_DELETE)
            ]
        ]
    )
    return keyboard