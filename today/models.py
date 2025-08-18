from enum import Enum
from datetime import datetime
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
    date_created: datetime = field(default_factory=datetime.now)
    date_completed: Optional[datetime] = None

    def mark_completed(self):
        self.status = TaskStatus.COMPLETED
        self.date_completed = datetime.now()