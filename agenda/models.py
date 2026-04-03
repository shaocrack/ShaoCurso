"""Modelos del sistema de agenda.

Los valores de los enums (prioridad y estado) están en español para
coincidir con la interfaz de usuario del CLI.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    """Prioridad de una tarea: baja, media o alta."""

    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class Status(str, Enum):
    """Estado de una tarea: pendiente o completada."""

    PENDING = "pendiente"
    DONE = "completada"


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    due_date: Optional[date] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority.value,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            priority=Priority(data.get("priority", Priority.MEDIUM.value)),
            status=Status(data.get("status", Status.PENDING.value)),
        )
