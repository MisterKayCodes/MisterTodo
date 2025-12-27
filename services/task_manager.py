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
    # Define valid priorities at the Manager level for business validation.
    VALID_PRIORITIES = {"Low", "Medium", "High"}

    def __init__(self):
        self.repo = TaskRepository()

    def _validate_priority(self, priority: str) -> str:
        """
        Rule 6: No 'smart' guessing. 
        Explicitly validate business rules before passing to durable storage.
        """
        if priority not in self.VALID_PRIORITIES:
            # We enforce a known state (Rule 1)
            return "Medium"
        return priority

    def add_task(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[str] = None,
        priority: str = "Medium",
        project: Optional[str] = None
    ) -> int:
        # Rule 6 & 14: Explicit validation at the entry point.
        validated_priority = self._validate_priority(priority)
        
        return self.repo.add_task(
            user_id=user_id, 
            name=name, 
            description=description or "", 
            due_date=due_date or "", 
            tags=tags, 
            priority=validated_priority, 
            project=project
        )

    def get_tasks(self, user_id: int) -> List[Task]:
        raw_tasks = self.repo.get_tasks(user_id)
        return [Task.from_dict(t) for t in raw_tasks]

    def get_completed_tasks(self, user_id: int, limit: int = 50) -> List[Task]:
        """Provides data for the Phase 2 Habit Stats engine."""
        raw_tasks = self.repo.get_completed_tasks(user_id, limit)
        return [Task.from_dict(t) for t in raw_tasks]

    def mark_task_done(self, task_id: int, user_id: int) -> bool:
        # Rule 1: Move the task from 'Active' to 'Completed' state.
        return self.repo.mark_task_done(task_id, user_id)

    def delete_task(self, task_id: int, user_id: int) -> bool:
        return self.repo.delete_task(task_id, user_id)
