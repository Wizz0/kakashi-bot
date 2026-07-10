import asyncio
from datetime import datetime, time, timedelta
from aiogram import Bot
from app import crud
from app.config import BOT_TOKEN, GROUP_CHAT_ID, TIMEZONE, REMINDER_HOUR, REMINDER_MINUTE, CHECK_HOUR, CHECK_MINUTE, SCHEDULE_DAY
from app.bot.keyboards import get_cleaned_keyboard

bot = Bot(token=BOT_TOKEN)

async def send_reminder():
    queue = await crud.get_today_queue()
    if queue:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"💩 {queue['name']}, убери какашки!",
            reply_markup=get_cleaned_keyboard(queue["id"])
        )

async def check_uncleaned():
    uncleaned = await crud.get_uncleaned_yesterday()
    for entry in uncleaned:
        await crud.add_penalty(entry["user_id"])
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"😾 {entry['name']} не убрал какашки! Прячь тапки, +1 штраф"
        )

async def generate_schedule():
    today = datetime.now(TIMEZONE).date()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = today + timedelta(days=days_until_monday)

    await crud.generate_week_schedule(next_monday)
    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"📅 Расписание на неделю сгенерировано!"
    )

async def scheduler_loop():
    while True:
        now = datetime.now(TIMEZONE)

        if now.hour == REMINDER_HOUR and now.minute == REMINDER_MINUTE:
            await send_reminder()
            await asyncio.sleep(60)
        
        if now.strftime("%A").lower() == SCHEDULE_DAY and now.hour == 0 and now.minute == 0:
            await generate_schedule()
            await asyncio.sleep(60)
        
        await asyncio.sleep(30)