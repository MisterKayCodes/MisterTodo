from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
import logging

# Rule 10: Observability
logger = logging.getLogger(__name__)

class HabitStats:
    """
    Engine for calculating user productivity metrics, streaks, and goal progress.
    Follows Rule 11 by separating core logic from the persistence layer.
    """

    def __init__(self, user_id: int, task_manager: Any, daily_goal: int = 5):
        """
        Initialize the stats engine.
        :param user_id: The Telegram ID of the user.
        :param task_manager: Instance of TaskManager (Dependency Injection).
        :param daily_goal: Target tasks per day. Must be > 0 (Rule 6).
        """
        self.user_id = user_id
        self.task_manager = task_manager
        
        # Rule 1: Enforce a valid system state - No zero/negative goals
        if daily_goal <= 0:
            logger.warning(f"Invalid daily_goal {daily_goal} for user {user_id}. Defaulting to 5.")
            self.daily_goal = 5
        else:
            self.daily_goal = daily_goal

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parses ISO 8601 strings into timezone-aware UTC datetime objects.
        :return: datetime object or datetime.min on failure (Rule 7).
        """
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError) as e:
            logger.error(f"Rule 12 Error: Failed to parse date '{date_str}': {e}")
            return datetime.min.replace(tzinfo=timezone.utc)

    def get_recent_completions(self, days: int = 30) -> List[Any]:
        """
        Fetches Task objects completed within the specified lookback period.
        :param days: Number of days to look back.
        :return: List of Task dataclass objects.
        """
        all_completed = self.task_manager.get_completed_tasks(self.user_id, limit=500)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        return [
            t for t in all_completed 
            if t.completed_at and self._parse_date(t.completed_at) >= cutoff
        ]

    def get_daily_counts(self, days: int = 30) -> Dict[str, int]:
        """
        Aggregates completion counts by calendar day.
        :return: Dictionary mapping 'YYYY-MM-DD' -> completion_count.
        """
        tasks = self.get_recent_completions(days)
        counts: Dict[str, int] = {}
        for t in tasks:
            date_key = self._parse_date(t.completed_at).date().isoformat()
            counts[date_key] = counts.get(date_key, 0) + 1
        return counts

    def get_current_streak(self) -> int:
        """
        Calculates consecutive days of activity including today/yesterday.
        :return: Current streak count as an integer.
        """
        counts = self.get_daily_counts(days=365)
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        
        # Rule 6: If no activity today AND yesterday, the streak is broken.
        if counts.get(today.isoformat(), 0) == 0 and counts.get(yesterday.isoformat(), 0) == 0:
            return 0

        streak = 0
        for i in range(0, 365):
            day_str = (today - timedelta(days=i)).isoformat()
            if counts.get(day_str, 0) > 0:
                streak += 1
            else:
                # Rule 4: If we haven't done a task TODAY yet, don't break the streak.
                if i == 0: continue 
                break
        return streak

    def get_progress_stats(self) -> Dict[str, Any]:
        """
        Calculates current day progress against the user's daily goal.
        :return: Dict containing 'count', 'goal', 'percent' (float), and 'is_goal_reached' (bool).
        """
        today_str = datetime.now(timezone.utc).date().isoformat()
        counts = self.get_daily_counts(days=1)
        done_today = counts.get(today_str, 0)
        
        # Rule 5: Idempotent and predictable result
        return {
            "count": done_today,
            "goal": self.daily_goal,
            "percent": min(done_today / self.daily_goal, 1.0),
            "is_goal_reached": done_today >= self.daily_goal
        }
