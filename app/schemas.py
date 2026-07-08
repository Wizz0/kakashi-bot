from datetime import date
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Тег пользователя")

class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class UserResponse(BaseModel):
    id: int
    name: str
    penalties: int

class QueueResponse(BaseModel):
    id: int
    date: date
    is_cleaned: bool
    user_name: str | None = None

class QueueEntry(BaseModel):
    date: date
    user_id: int
    name: str

class ScheduleResponse(BaseModel):
    start_date: date

class ScheduleResponse(BaseModel):
    schedule: list[QueueEntry]

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str