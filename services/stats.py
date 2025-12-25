
import datetime
from typing import Optional, List, Dict
from services.persistence import TaskRepository


class HabitStats:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def _parse_iso(self, iso_str: Optional[str]) -> Optional[datetime.datetime]:
        """
        Parse ISO datetime string to timezone-aware datetime object.
        Handles formats: 2023-12-24T20:36:18.690192+00:00, 2023-12-24T20:36:18Z, etc.
        """
        if not iso_str:
            return None
        
        try:
            # Try parsing directly (handles most ISO formats)
            dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            
            # Ensure timezone awareness
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            
            return dt
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse datetime '{iso_str}': {e}")
            return None

    def seven_day_consistency(self, user_id: int) -> float:
        """
        Percentage of tasks that were completed out of all tasks
        that were *active* in the last 7 days.
        
        Active means: created within last 7 days AND not deleted.
        Completed means: completed within last 7 days.
        """
        tasks = self.task_repo.get_all_user_tasks(user_id)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        window_start = now - datetime.timedelta(days=7)
        
        active_tasks = []
        for task in tasks:
            created = self._parse_iso(task.get("created_at"))
            
            # Skip if no creation date or was created before window
            if not created or created < window_start:
                continue
                
            # Consider task active only if it was created in the window
            # (regardless of completion status)
            active_tasks.append(task)
        
        if not active_tasks:
            return 0.0
        
        completed_count = 0
        for task in active_tasks:
            is_completed = task.get("is_completed")
            completed_at = self._parse_iso(task.get("completed_at"))
            
            # Task is considered completed if:
            # 1. is_completed == 1 (or True)
            # 2. AND was completed within the window (or has no completion date)
            if is_completed in (1, True):
                if completed_at is None or completed_at >= window_start:
                    completed_count += 1
        
        percentage = (completed_count / len(active_tasks)) * 100
        return round(percentage, 1)

    def power_streak(self, user_id: int) -> int:
        """Consecutive days with at least one completed task, ending today."""
        tasks = self.task_repo.get_all_user_tasks(user_id)
        
        # Get unique dates when tasks were completed
        completed_dates = set()
        for task in tasks:
            if task.get("is_completed") in (1, True):
                completed_at = self._parse_iso(task.get("completed_at"))
                if completed_at:
                    completed_dates.add(completed_at.date())
        
        if not completed_dates:
            return 0
        
        # Sort dates in descending order
        sorted_dates = sorted(completed_dates, reverse=True)
        
        # Calculate the longest consecutive streak ending today or most recent completion
        today = datetime.date.today()
        max_streak = 0
        current_streak = 0
        
        # Start from today and go backwards
        check_date = today
        while True:
            if check_date in completed_dates:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
                check_date -= datetime.timedelta(days=1)
            else:
                # Break if we find a gap
                break
        
        return max_streak

    def get_streak_details(self, user_id: int) -> Dict:
        """Get detailed streak information."""
        tasks = self.task_repo.get_all_user_tasks(user_id)
        
        completed_dates = set()
        for task in tasks:
            if task.get("is_completed") in (1, True):
                completed_at = self._parse_iso(task.get("completed_at"))
                if completed_at:
                    completed_dates.add(completed_at.date())
        
        if not completed_dates:
            return {"current_streak": 0, "last_completion": None, "all_dates": []}
        
        sorted_dates = sorted(completed_dates)
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        current_streak = 0
        check_date = today
        
        # Calculate current streak (consecutive days up to today)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
        
        return {
            "current_streak": current_streak,
            "longest_streak": self._calculate_longest_streak(sorted_dates),
            "last_completion": max(completed_dates) if completed_dates else None,
            "completion_count": len(completed_dates),
            "all_dates": sorted(completed_dates)
        }
    
    def _calculate_longest_streak(self, sorted_dates: List[datetime.date]) -> int:
        """Calculate the longest streak from sorted list of dates."""
        if not sorted_dates:
            return 0
        
        longest = 1
        current = 1
        
        for i in range(1, len(sorted_dates)):
            prev_date = sorted_dates[i - 1]
            curr_date = sorted_dates[i]
            
            # Check if dates are consecutive
            if (curr_date - prev_date).days == 1:
                current += 1
                longest = max(longest, current)
            elif curr_date != prev_date:  # Same day doesn't break streak
                current = 1
        
        return longest


# Love From Mister 💛