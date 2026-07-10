from datetime import date, datetime

from sqlalchemy import text
from app.config import TIMEZONE

from fastapi import APIRouter, HTTPException, Query
from app import crud
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    QueueResponse,
    ScheduleGenerate,
    ScheduleResponse,
    MessageResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api", tags=["API"])

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    user_id = await crud.add_user(user.name)
    return UserResponse(id=user_id, name=user.name, penalties=0)

@router.get("/users", response_model=list[UserResponse])
async def list_users():
    users = await crud.get_all_users()
    return [UserResponse(**u) for u in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    user_data = await crud.get_user_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    await crud.update_user(user_id, user.name)
    user_data["name"] = user.name
    return UserResponse(**user_data)

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int):
    deleted = await crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return MessageResponse(message=f"User {user_id} deleted")

@router.get("/queue/today", response_model=QueueResponse)
async def get_today_queue():
    queue = await crud.get_today_queue()
    if not queue:
        raise HTTPException(status_code=404, detail="No queue for today")
    
    return QueueResponse(
        id=queue["id"],
        date=queue["date"],
        user_id=queue["user_id"],
        is_cleaned=queue["is_cleaned"],
        user_name=queue["name"],
    )

@router.get("/queue/week", response_model=list[QueueResponse])
async def get_week_schedule(start_date: date | None = None):
    if start_date is None:
        start_date = datetime.now(TIMEZONE).date()
    
    schedule = await crud.get_week_schedule(start_date)
    return [
        QueueResponse(
            id=entry["id"],
            date=entry["date"],
            user_id=entry["user_id"],
            is_cleaned=entry["is_cleaned"],
            user_name=entry["name"],
        )
        for entry in schedule
    ]

@router.get("queue/my", response_model=list[QueueResponse])
async def get_my_queue(user_id: int, start_date: date | None = None):
    if start_date is None:
        start_date = datetime.now(TIMEZONE).date()
    
    queue = await crud.get_user_queue(user_id, start_date)
    return [
        QueueResponse(
            id=0,
            date=entry["date"],
            user_id=user_id,
            is_cleaned=entry["is_cleaned"],
        )
        for entry in queue
    ]

@router.post("/schedule/generate", response_model=ScheduleResponse)
async def generate_schedule(data: ScheduleGenerate):
    schedule = await crud.generate_week_schedule(data.start_date)
    return ScheduleResponse(
        schedule=[
            {"date": entry["date"], "user_id": entry["user_id"], "name":entry["name"]}
            for entry in schedule
        ]
    )

@router.post("/queue/add", response_model=QueueResponse)
async def add_queue_entry(date: str = Query(..., description="Дата в формате YYYY-MM-DD"), user_id: int = Query(...)):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await crud.add_queue(date, user_id)

    # Получаем созданную запись
    async with crud.engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, date, user_id, COALESCE(is_cleaned, 0) as is_cleaned FROM queue WHERE date = :date AND user_id = :user_id ORDER BY id DESC LIMIT 1"),
            {"date": date, "user_id": user_id}
        )
        row = result.fetchone()
    
    return QueueResponse(
        id=row[0],
        date=row[1],
        user_id=row[2],
        is_cleaned=row[3],
        user_name=user["name"]
    )

@router.post("/queue/{queue_id}/clean", response_model=MessageResponse)
async def mark_cleaned(queue_id: int):
    cleaned = await crud.mark_cleaned(queue_id)
    if not cleaned:
        raise HTTPException(status_code=404, detail="Queue entry not found or already cleaned")
    
    return MessageResponse(message="Marked as cleaned")

@router.post("/users/{user_id}/penalty", response_model=MessageResponse)
async def add_penalty(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await crud.add_penalty(user_id)
    return MessageResponse(message=f"Penalty added to {user['name']}")
