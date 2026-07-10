from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_cleaned_keyboard(queue_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Убрал какашки", callback_data=f"cleaned:{queue_id}")]
        ]
    )