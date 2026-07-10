import asyncio
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from app.database import init_db
from app.api.routes import router as api_router
from app.bot.handlers import router as bot_router
from app.bot.scheduler import schedule_loop
from app.config import API_HOST, API_PORT, BOT_TOKEN

app = FastAPI(title="Kakashi Bot API")
app.include_router(api_router)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(bot_router)

async def set_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="my_queue", description="Мои дни уборки")
    ])

async def main():
    await init_db()

    await set_bot_commands()

    asyncio.create_task(schedule_loop())

    config = uvicorn.Config(app, host=API_HOST, port=API_PORT, log_level="info")
    server = uvicorn.Server(config)

    async with bot:
        await dp.start_polling(bot)
        await server.serve()

if __name__ == "__main__":
    asyncio.run(main())