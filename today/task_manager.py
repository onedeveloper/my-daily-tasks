from typing import List, Optional
from datetime import datetime, timedelta

from .database import Database
from .models import Task, TaskStatus, Priority


class TaskManager:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def add_task(self, description: str) -> int:
        return self.db.add_task(description)

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db.get_task(task_id)

    def mark_task_done(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            task.mark_completed()
            self.db.update_task(task)
            return True
        return False

    def mark_task_working(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            task.mark_working()
            self.db.update_task(task)
            return True
        return False

    def block_task(self, task_id: int, reason: str) -> bool:
        task = self.get_task(task_id)
        if task:
            task.mark_blocked(reason)
            self.db.update_task(task)
            return True
        return False

    def unblock_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            task.unblock()
            self.db.update_task(task)
            return True
        return False

    def set_task_priority(self, task_id: int, priority: Priority) -> bool:
        task = self.get_task(task_id)
        if task:
            task.set_priority(priority)
            self.db.update_task(task)
            return True
        return False

    def add_task_tag(self, task_id: int, tag: str) -> bool:
        task = self.get_task(task_id)
        if task:
            task.add_tag(tag)
            self.db.update_task(task)
            return True
        return False

    def get_active_tasks(self) -> List[Task]:
        return self.db.get_active_tasks()

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return self.db.get_tasks_by_status(status)

    def get_yesterday_completed_tasks(self) -> List[Task]:
        return self.db.get_yesterday_completed()

    def get_today_working_tasks(self) -> List[Task]:
        return self.db.get_tasks_by_status(TaskStatus.WORKING)

    def get_today_pending_high_priority_tasks(self) -> List[Task]:
        tasks = self.db.get_tasks_by_status(TaskStatus.PENDING)
        return [t for t in tasks if t.priority == Priority.HIGH]

    def get_blocked_tasks(self) -> List[Task]:
        return self.db.get_tasks_by_status(TaskStatus.BLOCKED)

    def get_rolling_tasks(self) -> List[Task]:
        active_tasks = self.get_active_tasks()
        today = datetime.now().date()
        return [t for t in active_tasks 
                if t.status == TaskStatus.PENDING 
                and t.date_created.date() < today]

    def get_tasks_completed_in_days(self, days: int) -> List[Task]:
        return self.db.get_completed_in_days(days)

    def archive_old_completed_tasks(self, days: int) -> int:
        return self.db.archive_old_tasks(days)

    def get_productivity_stats(self, days: int) -> dict:
        completed = self.get_tasks_completed_in_days(days)
        all_tasks = self.db.get_all_tasks()
        
        total_tasks = len([t for t in all_tasks if not t.archived])
        completed_count = len(completed)
        pending_count = len(self.db.get_tasks_by_status(TaskStatus.PENDING))
        working_count = len(self.db.get_tasks_by_status(TaskStatus.WORKING))
        blocked_count = len(self.db.get_tasks_by_status(TaskStatus.BLOCKED))
        
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        avg_completion_time = 0
        if completed:
            times = []
            for task in completed:
                if task.date_started and task.date_completed:
                    delta = task.date_completed - task.date_started
                    times.append(delta.total_seconds() / 3600)  # hours
            if times:
                avg_completion_time = sum(times) / len(times)
        
        return {
            'total_tasks': total_tasks,
            'completed': completed_count,
            'pending': pending_count,
            'working': working_count,
            'blocked': blocked_count,
            'completion_rate': completion_rate,
            'avg_completion_hours': avg_completion_time,
            'days': days
        }

    def close(self):
        self.db.close()