from enum import Enum
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


class TaskStatus(Enum):
    PENDING = "pending"
    WORKING = "working"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    id: int
    description: str
    status: TaskStatus = TaskStatus.WORKING
    priority: Priority = Priority.MEDIUM
    tags: List[str] = field(default_factory=list)
    date_created: datetime = field(default_factory=datetime.now)
    date_started: Optional[datetime] = field(default_factory=datetime.now)
    date_completed: Optional[datetime] = None
    date_due: Optional[datetime] = None
    blocker_reason: Optional[str] = None
    archived: bool = False

    def mark_working(self):
        self.status = TaskStatus.WORKING
        if self.date_started is None:
            self.date_started = datetime.now()

    def mark_completed(self):
        self.status = TaskStatus.COMPLETED
        self.date_completed = datetime.now()

    def mark_blocked(self, reason: str):
        self.status = TaskStatus.BLOCKED
        self.blocker_reason = reason

    def unblock(self):
        self.status = TaskStatus.PENDING
        self.blocker_reason = None

    def set_priority(self, priority: Priority):
        self.priority = priority

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def archive(self):
        self.archived = True