from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .database import Database
from .models import Task, TaskStatus, Priority


class TaskManager:
    def __init__(self, db: Optional[Database] = None, simulated_date: Optional[str] = None):
        self.db = db or Database()
        self.simulated_date = simulated_date
    
    def add_task(self, description: str) -> int:
        return self.db.add_task(description)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db.get_task(task_id)
    
    
    def mark_task_done(self, task_id: int) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.mark_completed()
            self.db.update_task(task)
            return True
        return False
    
    def mark_task_working(self, task_id: int) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.mark_working()
            self.db.update_task(task)
            return True
        return False
    
    def block_task(self, task_id: int, reason: str) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.mark_blocked(reason)
            self.db.update_task(task)
            return True
        return False
    
    def unblock_task(self, task_id: int) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.unblock()
            self.db.update_task(task)
            return True
        return False
    
    def set_task_priority(self, task_id: int, priority: Priority) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.set_priority(priority)
            self.db.update_task(task)
            return True
        return False
    
    def add_task_tag(self, task_id: int, tag: str) -> bool:
        task = self.db.get_task(task_id)
        if task:
            task.add_tag(tag)
            self.db.update_task(task)
            return True
        return False
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active (non-completed) tasks"""
        return self.db.get_active_tasks()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        return self.db.get_tasks_by_status(status)
    
    def get_yesterday_completed_tasks(self) -> List[Task]:
        """Get completed tasks from yesterday"""
        return self.db.get_yesterday_completed()
    
    def get_yesterday_worked_tasks(self) -> List[Task]:
        """Get all tasks that were worked on yesterday (or last working day)"""
        return self.db.get_yesterday_worked()
    
    def get_today_working_tasks(self) -> List[Task]:
        """Get all tasks for today (both working and completed today)"""
        return self.db.get_today_worked()
    
    def get_today_pending_high_priority_tasks(self) -> List[Task]:
        """Get high priority pending tasks"""
        tasks = self.get_tasks_by_status(TaskStatus.PENDING)
        return [t for t in tasks if t.priority == Priority.HIGH]
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get blocked tasks"""
        return self.get_tasks_by_status(TaskStatus.BLOCKED)
    
    def get_rolling_tasks(self) -> List[Task]:
        """Rolling tasks section - now empty since working tasks auto-carry forward"""
        return []
    
    def get_tasks_completed_in_days(self, days: int) -> List[Task]:
        """Get tasks completed in the past N days"""
        return self.db.get_completed_in_days(days)
    
    def archive_old_completed_tasks(self, days: int) -> int:
        """Archive old completed tasks"""
        return self.db.archive_old_tasks(days)
    
    def get_productivity_stats(self, days: int) -> dict:
        """Get productivity statistics"""
        completed = self.db.get_completed_in_days(days)
        all_tasks = self.db.get_all_tasks()
        
        # Get counts by status from all tasks
        working_count = len([t for t in all_tasks if t.status == TaskStatus.WORKING])
        blocked_count = len([t for t in all_tasks if t.status == TaskStatus.BLOCKED])
        pending_count = len([t for t in all_tasks if t.status == TaskStatus.PENDING])
        
        total_tasks = len(all_tasks)
        completed_count = len(completed)
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed': completed_count,
            'pending': pending_count,
            'working': working_count,
            'blocked': blocked_count,
            'completion_rate': completion_rate,
            'avg_completion_hours': 0,  # Not implemented yet
            'days': days
        }
    
    def get_history(self, days: int = 7) -> Dict[str, List[Task]]:
        """Get task history for the past N days"""
        # For now, return completed tasks grouped by completion date
        completed_tasks = self.db.get_completed_in_days(days)
        history = {}
        
        for task in completed_tasks:
            if task.date_completed:
                day_key = task.date_completed.strftime('%Y-%m-%d')
                if day_key not in history:
                    history[day_key] = []
                history[day_key].append(task)
        
        return history