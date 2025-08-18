from enum import Enum
from datetime import date
from typing import Optional, List
from dataclasses import dataclass, field


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    date_created: date = field(default_factory=date.today)
    date_completed: Optional[date] = None

    def mark_completed(self):
        self.status = TaskStatus.COMPLETED
        self.date_completed = date.today()