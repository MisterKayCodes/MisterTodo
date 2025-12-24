import sqlite3
import logging
import os
from typing import List, Dict
from contextlib import contextmanager

# Rule 10: Observability
logger = logging.getLogger(__name__)

# --- Rule 13: Absolute Pathing (2025 Standard) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "db", "todo.sqlite")

class TaskRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def _connection(self):
        """Rule 7: Safe connection management with Health Checks."""
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
        """Rule 1: Ensure system starts in a known state."""
        with self._connection() as conn:
            # Fixed Column Name to 'is_completed' to match the handlers
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
        """Rule 2: Store critical state in durable storage."""
        query = "INSERT INTO tasks (user_id, name, description, due_date) VALUES (?, ?, ?, ?)"
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id, name, description, due_date))
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, user_id: int) -> List[Dict]:
        """Rule 4: Explicit retrieval logic."""
        query = """
            SELECT id, name, description, due_date, is_completed 
            FROM tasks 
            WHERE user_id = ? AND is_completed = 0 
            ORDER BY id DESC
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def mark_task_done(self, task_id: int, user_id: int) -> bool:
        """
        Updates task status. 
        Rule 11: Requires user_id to ensure ownership.
        """
        # Rule 5: Idempotency - only update if currently 0
        query = "UPDATE tasks SET is_completed = 1 WHERE id = ? AND user_id = ? AND is_completed = 0"
        
        with self._connection() as conn:
            cursor = conn.execute(query, (task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

# Love From Mister
