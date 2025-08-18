import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import json

from .models import Task, TaskStatus


class Database:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            data_dir = Path.home() / ".local" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "today.db"
        
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                date_created TIMESTAMP NOT NULL,
                date_completed TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                work_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                UNIQUE(task_id, work_date)
            )
        ''')
        
        # Create index for fast queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_work_sessions_date 
            ON work_sessions (work_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_work_sessions_task 
            ON work_sessions (task_id)
        ''')
        
        self.conn.commit()

    def _task_from_row(self, row) -> Task:
        return Task(
            id=row['id'],
            description=row['description'],
            status=TaskStatus(row['status']),
            date_created=datetime.fromisoformat(row['date_created']) if row['date_created'] else datetime.now(),
            date_completed=datetime.fromisoformat(row['date_completed']) if row['date_completed'] else None,
        )

    def add_task(self, description: str) -> int:
        task = Task(id=0, description=description)
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (description, status, date_created)
            VALUES (?, ?, ?)
        ''', (
            task.description,
            task.status.value,
            task.date_created.isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Task]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        return self._task_from_row(row) if row else None

    def update_task(self, task: Task):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks SET
                description = ?,
                status = ?,
                date_completed = ?
            WHERE id = ?
        ''', (
            task.description,
            task.status.value,
            task.date_completed.isoformat() if task.date_completed else None,
            task.id
        ))
        self.conn.commit()

    def get_all_tasks(self) -> List[Task]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY date_created DESC')
        return [self._task_from_row(row) for row in cursor.fetchall()]

    def get_active_tasks(self) -> List[Task]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status != ?
            ORDER BY date_created DESC
        ''', (TaskStatus.COMPLETED.value,))
        return [self._task_from_row(row) for row in cursor.fetchall()]

    
    def get_yesterday_worked(self) -> List[Task]:
        """Get tasks worked on during the last work session"""
        last_work_date = self.get_last_work_date()
        if not last_work_date:
            return []
        
        # Check if last work date is today - if so, go back one more work day
        today = datetime.now().strftime('%Y-%m-%d')
        if last_work_date.strftime('%Y-%m-%d') == today:
            # Find the previous work date before today
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT MAX(work_date) as prev_date FROM work_sessions
                WHERE work_date < ?
            ''', (today,))
            row = cursor.fetchone()
            if row and row['prev_date']:
                last_work_date = datetime.strptime(row['prev_date'], '%Y-%m-%d')
            else:
                return []  # No previous work sessions
        
        return self.get_tasks_worked_on_date(last_work_date)
    
    def get_today_worked(self) -> List[Task]:
        """Get tasks worked on today"""
        today = datetime.now()
        return self.get_tasks_worked_on_date(today)


    def record_work_session(self, task_id: int, work_date: Optional[datetime] = None):
        """Record that work was done on a task on a specific date"""
        if work_date is None:
            work_date = datetime.now()
        
        work_date_str = work_date.strftime('%Y-%m-%d')
        cursor = self.conn.cursor()
        
        # Use INSERT OR IGNORE to avoid duplicates
        cursor.execute('''
            INSERT OR IGNORE INTO work_sessions (task_id, work_date)
            VALUES (?, ?)
        ''', (task_id, work_date_str))
        self.conn.commit()

    def get_last_work_date(self) -> Optional[datetime]:
        """Get the most recent date when any work was done"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(work_date) as last_date FROM work_sessions
        ''')
        row = cursor.fetchone()
        if row and row['last_date']:
            return datetime.strptime(row['last_date'], '%Y-%m-%d')
        return None

    def get_tasks_worked_on_date(self, date: datetime) -> List[Task]:
        """Get all tasks that were worked on for a specific date"""
        date_str = date.strftime('%Y-%m-%d')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.* FROM tasks t
            JOIN work_sessions ws ON t.id = ws.task_id
            WHERE ws.work_date = ?
            ORDER BY ws.created_at DESC
        ''', (date_str,))
        return [self._task_from_row(row) for row in cursor.fetchall()]


    def close(self):
        self.conn.close()