from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app import crud
from datetime import datetime
from app.config import TIMEZONE

router = Router()

@router.message(F.chat.type == "private", F.text == "/my_queue")
async def my_queue_command(message: Message):
    user = await crud.get_user_by_name(f"@{message.from_user.username}")
    if not user:
        await message.answer("Тебя нет в списке рабов 😿")
        return
    
    today = datetime.now(TIMEZONE).date()

    queue = await crud.get_user_queue(user["id"], today)
    if not queue:
        await message.answer("На этой неделе у тебя нет дней уборки 🎉")
        return
    
    days = [entry["date"] for entry in queue]
    text = "📅 Твои дни уборки на этой неделе:\n\n"
    for day in days:
        text += f"- {day}\n"
    
    await message.answer(text)

@router.callback_query(F.data.startswith("cleaned:"))
async def cleaned_callback(callback: CallbackQuery):
    queue_id = int(callback.data.split(":")[1])

    cleaned = await crud.mark_cleaned(queue_id)
    if cleaned:
        await callback.message.edit_text(
            f"{callback.message.text}\n\n😺 Убрано!"
        )
        await callback.answer("Отмечено как убрано!")
    else:
        await callback.answer("Уже отмечено")