import aiosqlite
import os
from typing import List, Optional

class Database:
    def __init__(self, db_path: str = "db/database.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS product_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    
    async def add_url(self, article: str, url: str) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Используем INSERT OR IGNORE чтобы не перезаписывать существующие записи
                cursor = await db.execute(
                    "INSERT OR IGNORE INTO product_urls (article, url) VALUES (?, ?)",
                    (article, url)
                )
                await db.commit()
                # Возвращаем True только если была добавлена новая запись
                return cursor.rowcount > 0
        except Exception:
            return False
    
    async def get_all_urls(self) -> List[tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT article, url FROM product_urls ORDER BY id")
            return await cursor.fetchall()
    
    async def delete_by_articles(self, articles: List[str]) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ",".join("?" * len(articles))
            cursor = await db.execute(
                f"DELETE FROM product_urls WHERE article IN ({placeholders})",
                articles
            )
            await db.commit()
            return cursor.rowcount
    
    async def get_urls_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM product_urls")
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def article_exists(self, article: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT 1 FROM product_urls WHERE article = ?", (article,))
            result = await cursor.fetchone()
            return result is not None