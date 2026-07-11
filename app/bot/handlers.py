from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app import crud
from datetime import datetime, timedelta
from app.config import TIMEZONE

router = Router()

MONTHS = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }

async def format_date(date_str: str):
    year, month, day = map(int, date_str.split("-"))
    return f"{day} {MONTHS[month]}"

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

    schedule = await crud.get_week_schedule(monday)
    if not schedule:
        await message.answer("Расписание на эту неделю пустое 🙀")
        return
    
    text = f"📆 Расписание на неделю ({monday} - {monday + timedelta(days=6)}):\n\n"
    for entry in schedule:
        formatted_date = format_date(entry["date"])
        name = entry["name"]
        cleaned = "✔" if entry["is_cleaned"] else "❌"
        text += f"{formatted_date} - {name} {cleaned}\n"
    
    await message.answer(text)

@router.message(F.chat.type.in_(["group", "supergroup"]), Command("today_queue"))
async def today_queue_command(message: Message):
    today = await crud.get_today_queue()
    if not today:
        await message.answer("Расписание на сегодня пустое 🙀")
        return
    
    text = f"Cегодня убирает {today['name']}, смотри у меня! 😾"
    
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
        text += f"- {format_date(day)}\n"
    
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