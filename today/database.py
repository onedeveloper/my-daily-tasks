import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import json

from .models import Task, TaskStatus, Priority


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
                priority TEXT NOT NULL,
                tags TEXT,
                date_created TIMESTAMP NOT NULL,
                date_started TIMESTAMP,
                date_completed TIMESTAMP,
                date_due TIMESTAMP,
                blocker_reason TEXT,
                archived BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()

    def _task_from_row(self, row) -> Task:
        return Task(
            id=row['id'],
            description=row['description'],
            status=TaskStatus(row['status']),
            priority=Priority(row['priority']),
            tags=json.loads(row['tags']) if row['tags'] else [],
            date_created=datetime.fromisoformat(row['date_created']) if row['date_created'] else datetime.now(),
            date_started=datetime.fromisoformat(row['date_started']) if row['date_started'] else None,
            date_completed=datetime.fromisoformat(row['date_completed']) if row['date_completed'] else None,
            date_due=datetime.fromisoformat(row['date_due']) if row['date_due'] else None,
            blocker_reason=row['blocker_reason'],
            archived=bool(row['archived'])
        )

    def add_task(self, description: str) -> int:
        task = Task(id=0, description=description)
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (description, status, priority, tags, date_created, archived)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            task.description,
            task.status.value,
            task.priority.value,
            json.dumps(task.tags),
            task.date_created.isoformat(),
            task.archived
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
                priority = ?,
                tags = ?,
                date_started = ?,
                date_completed = ?,
                date_due = ?,
                blocker_reason = ?,
                archived = ?
            WHERE id = ?
        ''', (
            task.description,
            task.status.value,
            task.priority.value,
            json.dumps(task.tags),
            task.date_started.isoformat() if task.date_started else None,
            task.date_completed.isoformat() if task.date_completed else None,
            task.date_due.isoformat() if task.date_due else None,
            task.blocker_reason,
            task.archived,
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
            WHERE archived = 0 AND status != ?
            ORDER BY date_created DESC
        ''', (TaskStatus.COMPLETED.value,))
        return [self._task_from_row(row) for row in cursor.fetchall()]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = ? AND archived = 0
            ORDER BY date_created DESC
        ''', (status.value,))
        return [self._task_from_row(row) for row in cursor.fetchall()]

    def get_yesterday_completed(self) -> List[Task]:
        yesterday = datetime.now() - timedelta(days=1)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = ? AND date_completed >= ?
            ORDER BY date_completed DESC
        ''', (TaskStatus.COMPLETED.value, yesterday.isoformat()))
        return [self._task_from_row(row) for row in cursor.fetchall()]

    def get_completed_in_days(self, days: int) -> List[Task]:
        since = datetime.now() - timedelta(days=days)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = ? AND date_completed >= ?
            ORDER BY date_completed DESC
        ''', (TaskStatus.COMPLETED.value, since.isoformat()))
        return [self._task_from_row(row) for row in cursor.fetchall()]

    def archive_old_tasks(self, days: int) -> int:
        cutoff = datetime.now() - timedelta(days=days)
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks SET archived = 1
            WHERE status = ? AND date_completed < ? AND archived = 0
        ''', (TaskStatus.COMPLETED.value, cutoff.isoformat()))
        self.conn.commit()
        return cursor.rowcount

    def close(self):
        self.conn.close()