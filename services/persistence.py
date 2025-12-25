import sqlite3
import logging
import os
from typing import List, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "db", "todo.sqlite")


class TaskRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            yield conn
        except sqlite3.DatabaseError as e:
            logger.critical(f"DATABASE ERROR: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    def init_db(self):
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    is_completed INTEGER NOT NULL DEFAULT 0
                )
            """)
        logger.info("Database initialized and synchronized.")

    def add_task(self, user_id: int, name: str, description: str, due_date: str) -> int:
        query = """
            INSERT INTO tasks (user_id, name, description, due_date)
            VALUES (?, ?, ?, ?)
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id, name, description, due_date))
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, user_id: int) -> List[Dict]:
        query = """
            SELECT id, name, description, due_date, is_completed
            FROM tasks
            WHERE user_id = ? AND is_completed = 0
            ORDER BY id DESC
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    #DELETE
    def delete_task(self, task_id: int, user_id: int) -> bool:
        query = "DELETE FROM tasks WHERE id = ? AND user_id = ?"
        with self._connection() as conn:
            cursor = conn.execute(query, (task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    #EDIT
    def update_task_name(self, task_id: int, user_id: int, new_name: str) -> bool:
        query = """
            UPDATE tasks
            SET name = ?
            WHERE id = ? AND user_id = ? AND is_completed = 0
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (new_name, task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def mark_task_done(self, task_id: int, user_id: int) -> bool:
        query = """
            UPDATE tasks
            SET is_completed = 1
            WHERE id = ? AND user_id = ? AND is_completed = 0
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
