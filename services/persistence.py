import sqlite3
import logging
import os
from typing import List, Dict, Optional
from contextlib import contextmanager
from datetime import datetime, timezone

# Rule 10: Observability
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "db", "todo.sqlite")

class TaskRepository:
    # Rule 4: Explicit constants for business logic
    VALID_PRIORITIES = {"Low", "Medium", "High"}

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def _connection(self):
        # Rule 7 & 12: Recovery and Explicit Error Handling
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
        """
        Initializes the database with schema version tracking (Rule 1 & 17).
        """
        with self._connection() as conn:
            # 1. Create tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    is_completed INTEGER NOT NULL DEFAULT 0,
                    completed_at TEXT,
                    tags TEXT,
                    priority TEXT DEFAULT 'Medium',
                    project TEXT
                )
            """)
            
            # 2. Schema Evolution: Idempotent column check (Rule 5)
            # This handles cases where the table exists but lacks new Phase 1 columns
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row['name'] for row in cursor.fetchall()]
            
            migrations = {
                "tags": "TEXT",
                "priority": "TEXT DEFAULT 'Medium'",
                "project": "TEXT"
            }

            for col_name, col_type in migrations.items():
                if col_name not in columns:
                    conn.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
                    logger.info(f"Migration: Added missing column '{col_name}'")

            conn.commit()
        logger.info("Database initialized and synchronized.")

    def _validate_priority(self, priority: str):
        """Rule 14: Input validation to prevent bad data state."""
        if priority not in self.VALID_PRIORITIES:
            logger.warning(f"Invalid priority attempted: {priority}. Defaulting to 'Medium'.")
            return "Medium"
        return priority

    def add_task(
        self,
        user_id: int,
        name: str,
        description: str,
        due_date: str,
        tags: Optional[str] = None,
        priority: str = "Medium",
        project: Optional[str] = None
    ) -> int:
        # Validate before insertion (Rule 6)
        clean_priority = self._validate_priority(priority)
        
        query = """
            INSERT INTO tasks (user_id, name, description, due_date, tags, priority, project)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id, name, description, due_date, tags, clean_priority, project))
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, user_id: int) -> List[Dict]:
        """Rule 11: Business logic for active tasks."""
        query = """
            SELECT * FROM tasks
            WHERE user_id = ? AND is_completed = 0
            ORDER BY priority DESC, id DESC
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_completed_tasks(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Foundation for Phase 2: Habit Stats engine."""
        query = """
            SELECT * FROM tasks 
            WHERE user_id = ? AND is_completed = 1 
            ORDER BY completed_at DESC LIMIT ?
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def mark_task_done(self, task_id: int, user_id: int) -> bool:
        # Rule 13: 2025 Standard (Timezone-aware)
        now = datetime.now(timezone.utc).isoformat()
        query = """
            UPDATE tasks
            SET is_completed = 1, completed_at = ?
            WHERE id = ? AND user_id = ? AND is_completed = 0
        """
        with self._connection() as conn:
            cursor = conn.execute(query, (now, task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Physical deletion (Use only if user explicitly requests 'Reset' in Phase 3)."""
        query = "DELETE FROM tasks WHERE id = ? AND user_id = ?"
        with self._connection() as conn:
            cursor = conn.execute(query, (task_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
