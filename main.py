# main.py
from fastapi import FastAPI, HTTPException, Depends
import asyncpg
from config import DATABASE_URL

app = FastAPI()

# Функция для создания подключения к базе данных
async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Создание таблицы, если она не существует
@app.on_event("startup")
async def startup():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL
        )
    """)
    await conn.close()

@app.get("/entries/")
async def index():
    pass

# Маршрут для добавления новой записи в базу данных
@app.post("/entries/")
async def create_entry(content: str, conn=Depends(get_db_connection)):
    if content is None or content == '' or content == ' ':
        raise HTTPException(status_code=400, detail="Неправильные данные")
    query = "INSERT INTO entries(content) VALUES ($1) RETURNING id"
    try:
        entry_id = await conn.fetchval(query, content)
        return {"id": entry_id, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при добавлении записи")

# Маршрут для получения всех записей из базы данных
@app.get("/entries/")
async def get_entries(conn=Depends(get_db_connection)):
    query = "SELECT id, content FROM entries"
    try:
        rows = await conn.fetch(query)
        return [{"id": row["id"], "content": row["content"]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при получении записей")
