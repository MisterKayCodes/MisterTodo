import csv
import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from services.persistence import TaskRepository

@dataclass
class Task:
    id: int
    user_id: int
    name: str
    description: Optional[str]
    due_date: Optional[str]
    is_completed: bool
    completed_at: Optional[str]
    tags: Optional[str]
    priority: str
    project: Optional[str]

    @classmethod
    def from_dict(cls, data: dict):
        """Helper to create a Task from a DB row (Rule 8: Boring/Reliable)."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            name=data["name"],
            description=data.get("description"),
            due_date=data.get("due_date"),
            is_completed=bool(data.get("is_completed", 0)),
            completed_at=data.get("completed_at"),
            tags=data.get("tags"),
            priority=data.get("priority", "Medium"),
            project=data.get("project")
        )

class TaskManager:
    # Rule 4: Logic must be explicit.
    VALID_PRIORITIES = {"Low", "Medium", "High"}

    def __init__(self):
        self.repo = TaskRepository()

    def _validate_priority(self, priority: str) -> str:
        """Rule 6: Explicit business rule validation."""
        if priority not in self.VALID_PRIORITIES:
            return "Medium"
        return priority

    def add_task(self, user_id: int, name: str, **kwargs) -> int:
        """Rule 6 & 14: Input Sanitization and Entry Point."""
        priority = self._validate_priority(kwargs.get("priority", "Medium"))
        return self.repo.add_task(
            user_id=user_id,
            name=name,
            description=kwargs.get("description") or "",
            due_date=kwargs.get("due_date") or "",
            tags=kwargs.get("tags"),
            priority=priority,
            project=kwargs.get("project")
        )

    def get_tasks(self, user_id: int) -> List[Task]:
        """Fetches all active tasks."""
        raw_tasks = self.repo.get_tasks(user_id)
        return [Task.from_dict(t) for t in raw_tasks]

    def get_completed_tasks(self, user_id: int, limit: int = 500) -> List[Task]:
        """
        FIXED: Rule 11 Bridge for HabitStats.
        Resolves AttributeError by providing the full completion list.
        """
        raw_tasks = self.repo.get_completed_tasks(user_id, limit)
        return [Task.from_dict(t) for t in raw_tasks]

    def mark_task_done(self, task_id: int, user_id: int) -> bool:
        """Rule 1: Transition system state from Active to Done."""
        return self.repo.mark_task_done(task_id, user_id)

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Rule 5: Idempotent removal from durable storage."""
        return self.repo.delete_task(task_id, user_id)

    # --- Archive & Classification Logic ---

    def get_archive(self, user_id: int, page: int = 0) -> List[Task]:
        """Fetches paginated completed tasks for the Archive UI."""
        limit = 10
        offset = page * limit
        raw_tasks = self.repo.get_completed_tasks_paginated(user_id, limit, offset)
        return [Task.from_dict(t) for t in raw_tasks]

    def get_tasks_by_period(self, user_id: int, period: str) -> List[Task]:
        """
        Rule 11: Classify tasks by daily, weekly, or monthly periods.
        2025 Standard: Validated against Dec 27, 2025.
        """
        if period == "today":
            raw_tasks = self.repo.get_tasks_by_date_range(user_id, days=0)
        elif period == "weekly":
            raw_tasks = self.repo.get_tasks_by_date_range(user_id, days=7)
        elif period == "monthly":
            raw_tasks = self.repo.get_tasks_by_date_range(user_id, days=30)
        else:
            return []
        
        return [Task.from_dict(t) for t in raw_tasks]

    def export_tasks_to_csv(self, user_id: int) -> str:
        """
        Rule 2: Generate durable CSV report.
        Groups and sorts all completed tasks by date.
        """
        all_raw = self.repo.get_completed_tasks(user_id, limit=2000)
        all_tasks = [Task.from_dict(t) for t in all_raw]

        directory = "storage/exports"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"tasks_{user_id}.csv")

        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Completion Date", "Task Name", "Priority", "Project"])
            
            # Rule 8: Grouped sorting (Newest first)
            all_tasks.sort(key=lambda x: x.completed_at or "", reverse=True)
            
            for t in all_tasks:
                date_str = t.completed_at[:10] if t.completed_at else "Unknown"
                writer.writerow([date_str, t.name, t.priority, t.project or "General"])
                
        return file_path
