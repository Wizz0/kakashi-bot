import asyncio
import uvicorn
from fastapi import FastAPI
from app.database import init_db
from app.api.routes import router
from app.config import API_HOST, API_PORT

app = FastAPI(title="Kakashi Bot API")
app.include_router(router)

async def main():
    await init_db()

    config = uvicorn.Config(app, host=API_HOST, port=API_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())