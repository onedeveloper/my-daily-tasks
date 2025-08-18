from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .database import Database
from .models import Task, TaskStatus


class TaskManager:
    def __init__(self, db: Optional[Database] = None, simulated_date: Optional[str] = None):
        self.db = db or Database()
        self.simulated_date = simulated_date
    
    def add_task(self, description: str) -> int:
        task_id = self.db.add_task(description)
        # Record work session for today when creating a task
        self.db.record_work_session(task_id)
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db.get_task(task_id)
    
    
    def mark_task_done(self, task_id: int) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.mark_completed()
            self.db.update_task(task)
            # Record work session for today
            self.db.record_work_session(task_id)
            return True
        return False
    
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active (non-completed) tasks"""
        return self.db.get_active_tasks()
    
    def get_yesterday_worked_tasks(self) -> List[Task]:
        """Get all tasks that were worked on yesterday (or last working day)"""
        return self.db.get_yesterday_worked()
    
    def get_today_working_tasks(self) -> List[Task]:
        """Get all tasks for today (both working and completed today)"""
        return self.db.get_today_worked()