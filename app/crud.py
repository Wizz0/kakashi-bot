from datetime import date, datetime, timedelta
from sqlalchemy import text
from app.database import engine
from app.config import TIMEZONE

def get_today() -> date:
    return datetime.now(TIMEZONE).date()

async def add_user(name: str) -> int:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("INSERT INTO users (name) VALUES (:name, 0) RETURNING id"),
            {"name": name}
        )
        await conn.commit()
        return result.scalar()

async def delete_user(user_id: int) -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": user_id}
        )
        await conn.commit()
        return result.rowcount > 0

async def update_user(user_id: int, name: str) -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("UPDATE users SET name = :name WHERE id = :id"),
            {"name": name, "id": user_id}
        )
        await conn.commit()
        return result.rowcount > 0

async def get_all_users() -> list[dict]:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, name, COALESCE(penalties, 0) FROM users"))
        rows = result.fetchall()
        return [{"id": row[0], "name": row[1], "penalties": row[2]} for row in rows]

async def get_user_by_id(user_id: int) -> dict | None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, name, penalties FROM users WHERE id = :id"),
            {"id": user_id}
        )
        row = result.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "penalties": row[2]}
        return None

async def get_user_by_name(name: str) -> dict | None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, name, penalties FROM users WHERE name = :name"),
            {"name": name}
        )
        row = result.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "penalties": row[2]}
        return None

async def get_today_queue() -> dict | None:
    today = get_today()
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT q.id, q.date, q.user_id, COALESCE(q.is_cleaned, 0) as is_cleaned, u.name
                FROM queue q
                JOIN users u ON q.user_id = u.id
                WHERE q.date = :today
            """),
            {"today": today}
        )
        row = result.fetchone()
        if row:
            return {"id": row[0], "date": row[1], "user_id": row[2], "is_cleaned": bool(row[3]), "name": row[4]}
        return None

async def mark_cleaned(queue_id: int) -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("UPDATE queue SET is_cleaned = 1 WHERE id = :id AND is_cleaned = 0"),
            {"id": queue_id}
        )
        await conn.commit()
        return result.rowcount > 0

async def get_uncleaned_yesterday() -> list[dict]:
    yesterday = (get_today() - timedelta(days=1)).isoformat()
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT q.id, q.user_id, u.name
                FROM queue q
                JOIN users u ON q.user_id = u.id
                WHERE q.date = :yesterday AND q.is_cleaned = 0
            """),
            {"yesterday": yesterday}
        )
        rows = result.fetchall()
        return [{"id": row[0], "user_id": row[1], "name": row[2]} for row in rows]
    
async def add_penalty(user_id: int) -> None:
    async with engine.connect() as conn:
        await conn.execute(
            text("UPDATE users SET penalties = penalties + 1 WHERE id = :id"),
            {"id": user_id}
        )
        await conn.commit()

async def clear_penalties(user_id: int) -> None:
    async with engine.connect() as conn:
        await conn.execute(
            text("UPDATE users SET penalties = 0 WHERE id = :id"),
            {"id": user_id}
        )
        await conn.commit()

async def get_last_user(start_date: date):
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id FROM queue 
                WHERE date < :start_date 
                ORDER BY date DESC, id DESC 
                LIMIT 1
            """),
            {"start_date": start_date.isoformat()}
        )
        row = result.fetchone()
        if row:
            return row[0]
        return None
    
async def add_queue(date: date, user_id: int):
    async with engine.connect() as conn:
        await conn.execute(
            text("INSERT INTO queue (date, user_id) VALUES (:date, :user_id)"),
            {"date": date, "user_id": user_id}
        )
        await conn.commit()
    
async def generate_week_schedule(start_date: date) -> list[dict]:
    async with engine.connect() as conn:
        users = await get_all_users()

        if not users:
            return []
        
        schedule = []
        
        super_penalty = next((u for u in users if u["penalties"] > 2), None)

        if super_penalty:
            for i in range(7):
                current_date = start_date + timedelta(days=i)
                schedule.append({
                    "date": current_date.isoformat(),
                    "user_id": super_penalty["id"],
                    "name": super_penalty["name"]
                })
            await clear_penalties(super_penalty["id"])

        else:
            last_user_id = await get_last_user(start_date)
            
            if last_user_id:
                last_index = next(i for i, u in enumerate(users) if u["id"] == last_user_id)
                start_index = (last_index + 1) % len(users)
            else:
                start_index = 0

            current_day = start_date
            user_index = start_index
            days_filled = 0

            while days_filled < 7:
                user = users[user_index % len(users)]

                schedule.append({
                    "date": current_day.isoformat(),
                    "user_id": user["id"],
                    "name": user["name"]
                })
                current_day += timedelta(days=1)
                days_filled += 1

                if user["penalties"] > 0:
                    for _ in range(user["penalties"]):
                        if days_filled >= 7:
                            break
                        schedule.append({
                            "date": current_day.isoformat(),
                            "user_id": user["id"],
                            "name": user["name"]
                        })
                        current_day += timedelta(days=1)
                        days_filled += 1
                    await clear_penalties(user["id"])

                user_index += 1

        for entry in schedule:
            await add_queue(entry["date"], entry["user_id"])

    return schedule

async def get_week_schedule(start_date: date) -> list[dict]:
    end_date = (start_date + timedelta(days=6)).isoformat()
    start_date_str = start_date.isoformat()
    
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT q.id, q.date, q.user_id, COALESCE(q.is_cleaned, 0) as is_cleaned, u.name
                FROM queue q
                JOIN users u ON q.user_id = u.id
                WHERE q.date BETWEEN :start AND :end
                ORDER BY q.date
            """),
            {"start": start_date_str, "end": end_date}
        )
        rows = result.fetchall()
        return [
            {"id": row[0], "date": row[1], "user_id": row[2], "is_cleaned": bool(row[3]), "name": row[4]}
            for row in rows
        ]

async def get_user_queue(user_id: int, start_date: date) -> list[dict]:
    end_date = (start_date + timedelta(days=6)).isoformat()
    start_date_str = start_date.isoformat()
    
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT q.date, COALESCE(q.is_cleaned, 0) as is_cleaned
                FROM queue q
                WHERE q.user_id = :user_id AND q.date BETWEEN :start AND :end
                ORDER BY q.date
            """),
            {"user_id": user_id, "start": start_date_str, "end": end_date}
        )
        rows = result.fetchall()
        return [{"date": row[0], "is_cleaned": bool(row[1])} for row in rows]