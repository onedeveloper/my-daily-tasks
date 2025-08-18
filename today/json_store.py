import json
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import asdict, dataclass
from .models import Task, TaskStatus, Priority


class JSONStore:
    def __init__(self, data_path: Optional[Path] = None, simulated_date: Optional[str] = None):
        if data_path is None:
            data_dir = Path.home() / ".local" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            data_path = data_dir / "today.json"
        
        self.data_path = data_path
        self.simulated_date = simulated_date
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        if not self.data_path.exists():
            return {}
        
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_data(self):
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def _get_today_key(self) -> str:
        if self.simulated_date:
            return self.simulated_date
        return str(date.today())
    
    def _get_yesterday_key(self) -> str:
        if self.simulated_date:
            sim_date = datetime.strptime(self.simulated_date, '%Y-%m-%d').date()
            return str(sim_date - timedelta(days=1))
        return str(date.today() - timedelta(days=1))
    
    def _get_last_working_day_key(self) -> Optional[str]:
        """Get the most recent day with data before today"""
        if not self.data:
            return None
        
        today = self._get_today_key()
        # Get all dates that are before today
        past_dates = [d for d in self.data.keys() if d < today]
        
        if past_dates:
            return max(past_dates)
        return None
    
    def _ensure_today_exists(self):
        """Ensure today has an entry, copying forward incomplete tasks if needed"""
        today = self._get_today_key()
        
        if today not in self.data:
            last_day = self._get_last_working_day_key()
            
            if last_day and last_day in self.data:
                # Copy forward incomplete tasks
                last_tasks = self.data[last_day].get('tasks', [])
                tasks_to_copy = []
                
                for task_data in last_tasks:
                    # Copy tasks that are working or blocked (not completed)
                    if task_data.get('status') in ['working', 'blocked']:
                        task_copy = task_data.copy()
                        tasks_to_copy.append(task_copy)
                
                self.data[today] = {'tasks': tasks_to_copy}
            else:
                self.data[today] = {'tasks': []}
            
            self._save_data()
    
    def _get_next_id(self) -> int:
        """Get the next available task ID"""
        max_id = 0
        for day_data in self.data.values():
            for task in day_data.get('tasks', []):
                task_id = task.get('id', 0)
                if task_id > max_id:
                    max_id = task_id
        return max_id + 1
    
    def add_task(self, description: str) -> int:
        """Add a new task to today"""
        self._ensure_today_exists()
        today = self._get_today_key()
        
        task_id = self._get_next_id()
        task = {
            'id': task_id,
            'description': description,
            'status': 'working',
            'priority': 'medium',
            'tags': [],
            'date_created': today,  # Just date, no time
            'date_started': today,  # Just date, no time
            'date_completed': None,
            'blocker_reason': None
        }
        
        self.data[today]['tasks'].append(task)
        self._save_data()
        return task_id
    
    def get_today_tasks(self) -> List[Dict]:
        """Get all tasks for today"""
        self._ensure_today_exists()
        today = self._get_today_key()
        return self.data[today].get('tasks', [])
    
    def get_yesterday_tasks(self) -> List[Dict]:
        """Get all tasks from yesterday (if it exists)"""
        yesterday = self._get_yesterday_key()
        if yesterday in self.data:
            return self.data[yesterday].get('tasks', [])
        return []
    
    def get_last_working_day_tasks(self) -> List[Dict]:
        """Get tasks from the last working day"""
        last_day = self._get_last_working_day_key()
        if last_day and last_day != self._get_today_key():
            return self.data[last_day].get('tasks', [])
        return []
    
    def update_task(self, task_id: int, updates: Dict) -> bool:
        """Update a task in today's list"""
        self._ensure_today_exists()
        today = self._get_today_key()
        
        tasks = self.data[today]['tasks']
        for i, task in enumerate(tasks):
            if task['id'] == task_id:
                tasks[i].update(updates)
                self._save_data()
                return True
        return False
    
    def mark_task_done(self, task_id: int) -> bool:
        """Mark a task as completed"""
        today = self._get_today_key()
        return self.update_task(task_id, {
            'status': 'completed',
            'date_completed': today  # Just date, no time
        })
    
    def mark_task_working(self, task_id: int) -> bool:
        """Mark a task as working"""
        today = self._get_today_key()
        return self.update_task(task_id, {
            'status': 'working',
            'date_started': today  # Just date, no time
        })
    
    def block_task(self, task_id: int, reason: str) -> bool:
        """Block a task with a reason"""
        return self.update_task(task_id, {
            'status': 'blocked',
            'blocker_reason': reason
        })
    
    def unblock_task(self, task_id: int) -> bool:
        """Unblock a task"""
        return self.update_task(task_id, {
            'status': 'working',
            'blocker_reason': None
        })
    
    def set_task_priority(self, task_id: int, priority: str) -> bool:
        """Set task priority"""
        return self.update_task(task_id, {'priority': priority})
    
    def add_task_tag(self, task_id: int, tag: str) -> bool:
        """Add a tag to a task"""
        self._ensure_today_exists()
        today = self._get_today_key()
        
        tasks = self.data[today]['tasks']
        for task in tasks:
            if task['id'] == task_id:
                if 'tags' not in task:
                    task['tags'] = []
                if tag not in task['tags']:
                    task['tags'].append(tag)
                    self._save_data()
                    return True
        return False
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID from today"""
        tasks = self.get_today_tasks()
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_history(self, days: int = 7) -> Dict[str, List[Dict]]:
        """Get task history for the past N days"""
        result = {}
        for day_key in sorted(self.data.keys(), reverse=True)[:days]:
            result[day_key] = self.data[day_key].get('tasks', [])
        return result
    
    def get_week_summary(self) -> Dict[str, List[Dict]]:
        """Get tasks for the current week"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        week_data = {}
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_key = str(day)
            if day_key in self.data:
                week_data[day_key] = self.data[day_key].get('tasks', [])
        
        return week_data