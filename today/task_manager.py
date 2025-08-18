from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .json_store import JSONStore
from .models import Task, TaskStatus, Priority


class TaskManager:
    def __init__(self, store: Optional[JSONStore] = None, simulated_date: Optional[str] = None):
        self.store = store or JSONStore(simulated_date=simulated_date)
    
    def add_task(self, description: str) -> int:
        return self.store.add_task(description)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        task_data = self.store.get_task(task_id)
        if task_data:
            return self._task_from_dict(task_data)
        return None
    
    def _task_from_dict(self, data: Dict) -> Task:
        """Convert dictionary to Task object"""
        def parse_date(date_str):
            if not date_str:
                return None
            # Handle both date-only and datetime formats
            try:
                # Try date-only format first (YYYY-MM-DD)
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # Fall back to full datetime
                return datetime.fromisoformat(date_str)
        
        return Task(
            id=data.get('id', 0),
            description=data.get('description', ''),
            status=TaskStatus(data.get('status', 'working')),
            priority=Priority(data.get('priority', 'medium')),
            tags=data.get('tags', []),
            date_created=parse_date(data.get('date_created')) or datetime.now(),
            date_started=parse_date(data.get('date_started')),
            date_completed=parse_date(data.get('date_completed')),
            date_due=None,  # Not implemented in JSON store yet
            blocker_reason=data.get('blocker_reason'),
            archived=False  # Not used in JSON store
        )
    
    def mark_task_done(self, task_id: int) -> bool:
        return self.store.mark_task_done(task_id)
    
    def mark_task_working(self, task_id: int) -> bool:
        return self.store.mark_task_working(task_id)
    
    def block_task(self, task_id: int, reason: str) -> bool:
        return self.store.block_task(task_id, reason)
    
    def unblock_task(self, task_id: int) -> bool:
        return self.store.unblock_task(task_id)
    
    def set_task_priority(self, task_id: int, priority: Priority) -> bool:
        return self.store.set_task_priority(task_id, priority.value)
    
    def add_task_tag(self, task_id: int, tag: str) -> bool:
        return self.store.add_task_tag(task_id, tag)
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active (non-completed) tasks for today"""
        tasks_data = self.store.get_today_tasks()
        tasks = [self._task_from_dict(t) for t in tasks_data]
        return [t for t in tasks if t.status != TaskStatus.COMPLETED]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get today's tasks by status"""
        tasks_data = self.store.get_today_tasks()
        tasks = [self._task_from_dict(t) for t in tasks_data]
        return [t for t in tasks if t.status == status]
    
    def get_yesterday_completed_tasks(self) -> List[Task]:
        """Get completed tasks from yesterday"""
        tasks_data = self.store.get_yesterday_tasks()
        tasks = [self._task_from_dict(t) for t in tasks_data]
        return [t for t in tasks if t.status == TaskStatus.COMPLETED]
    
    def get_yesterday_worked_tasks(self) -> List[Task]:
        """Get all tasks that were worked on yesterday (or last working day)"""
        # Get the last working day's tasks (not literally yesterday)
        tasks_data = self.store.get_last_working_day_tasks()
        
        return [self._task_from_dict(t) for t in tasks_data]
    
    def get_today_working_tasks(self) -> List[Task]:
        """Get all tasks for today (both working and completed today)"""
        tasks_data = self.store.get_today_tasks()
        return [self._task_from_dict(t) for t in tasks_data]
    
    def get_today_pending_high_priority_tasks(self) -> List[Task]:
        """Get high priority pending tasks"""
        tasks_data = self.store.get_today_tasks()
        tasks = [self._task_from_dict(t) for t in tasks_data]
        return [t for t in tasks 
                if t.status == TaskStatus.PENDING and t.priority == Priority.HIGH]
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get blocked tasks"""
        return self.get_tasks_by_status(TaskStatus.BLOCKED)
    
    def get_rolling_tasks(self) -> List[Task]:
        """Rolling tasks section - now empty since working tasks auto-carry forward"""
        return []
    
    def get_tasks_completed_in_days(self, days: int) -> List[Task]:
        """Get tasks completed in the past N days"""
        history = self.store.get_history(days)
        completed_tasks = []
        
        for day_key, tasks_data in history.items():
            for task_data in tasks_data:
                if task_data.get('status') == 'completed':
                    completed_tasks.append(self._task_from_dict(task_data))
        
        return completed_tasks
    
    def archive_old_completed_tasks(self, days: int) -> int:
        """Archive is not needed with JSON store - we keep full history"""
        return 0
    
    def get_productivity_stats(self, days: int) -> dict:
        """Get productivity statistics"""
        history = self.store.get_history(days)
        
        total_tasks = 0
        completed_count = 0
        working_count = 0
        blocked_count = 0
        
        for day_key, tasks_data in history.items():
            for task_data in tasks_data:
                total_tasks += 1
                status = task_data.get('status')
                if status == 'completed':
                    completed_count += 1
                elif status == 'working':
                    working_count += 1
                elif status == 'blocked':
                    blocked_count += 1
        
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed': completed_count,
            'pending': 0,  # No pending in new model
            'working': working_count,
            'blocked': blocked_count,
            'completion_rate': completion_rate,
            'avg_completion_hours': 0,  # Not tracking this anymore
            'days': days
        }
    
    def get_history(self, days: int = 7) -> Dict[str, List[Task]]:
        """Get task history for the past N days"""
        history_data = self.store.get_history(days)
        history = {}
        
        for day_key, tasks_data in history_data.items():
            history[day_key] = [self._task_from_dict(t) for t in tasks_data]
        
        return history