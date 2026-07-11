from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app import crud
from datetime import datetime, timedelta
from app.config import TIMEZONE

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    text = (
        "Привет! Я бот для отслеживания уборки кошачьего лотка (да, ужасная судьба)\n\n"
        "<b>Что я умею:</b>\n"
        "• Каждый вечер в 20:00 напоминаю в группе, чья очередь убирать\n"
        "• Слежу, кто убрал, а кто нет\n"
        "• Начисляю штрафы за невыполненную уборку\n"
        "• <s>Казню штрафников</s>\n"
        "• Составляю расписание на неделю с учетом штрафов\n\n"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.chat.type.in_(["group", "supergroup"]), Command("week_queue"))
async def week_queue_command(message: Message):
    now = datetime.now(TIMEZONE)
    monday = now.date() - timedelta(days=now.weekday())
    #today = datetime.now(TIMEZONE).date()

    schedule = await crud.get_week_schedule(monday)
    #schedule = await crud.get_week_schedule(today)
    if not schedule:
        await message.answer("Расписание на эту неделю пустое 🙀")
        return
    
    text = f"📆 Расписание на неделю ({monday} - {monday + timedelta(days=6)}):\n\n"
    for entry in schedule:
        date_str = entry["date"]
        name = entry["name"]
        cleaned = "✔" if entry["is_cleaned"] else "❌"
        text += f"{date_str} - {name} {cleaned}\n"
    
    await message.answer(text)

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

@router.message(F.chat.type == "private", Command("my_penalties"))
async def my_penalties_command(message: Message):
    user = await crud.get_user_by_name(f"@{message.from_user.username}")
    if not user:
        await message.answer("Тебя нет в списке рабов 😿")
        return
    
    penalties = user["penalties"] or 0
    
    if penalties == 0:
        text = "😻 У тебя нет штрафов, так держать!"
    
    elif penalties > 0 and penalties <= 2:
        text = f"😾 Твои штрафы: {penalties}, будешь убирать столько дополнительных дней на следующей неделе"
    
    else:
        text = f"🙀 У тебя слишком много штрафов: {penalties}, будешь убирать всю следующую неделю"

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