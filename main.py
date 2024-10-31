# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
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

@app.get("/")
async def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Главная страница</title>
    </head>
    <body>
        <h1>Добро пожаловать в FastAPI приложение!</h1>
        <p>Это приложение для работы с записями в базе данных PostgreSQL.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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

@app.delete("/entries/")
async def delete_all_entries(conn=Depends(get_db_connection)):
    query = "DELETE FROM entries"
    try:
        await conn.execute(query)
        return {"message": "Все записи успешно удалены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении записей")
    
# Маршрут для удаления конкретной записи по ID
@app.delete("/entries/{id}")
async def delete_entry(id: int, conn=Depends(get_db_connection)):
    query = "DELETE FROM entries WHERE id = $1"
    try:
        result = await conn.execute(query, id)
        if result == "DELETE 0":  # Если запись не найдена
            raise HTTPException(status_code=404, detail="Запись с таким ID не найдена")
        return {"message": f"Запись с ID {id} успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении записи")
