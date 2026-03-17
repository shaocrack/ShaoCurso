import json
from datetime import date
from pathlib import Path
from typing import List, Optional

from .models import Priority, Status, Task


class Agenda:
    """Sistema de agenda para gestionar tareas pendientes."""

    def __init__(self, storage_path: str = "agenda_data.json"):
        self._storage_path = Path(storage_path)
        self._tasks: List[Task] = []
        self._next_id: int = 1
        self._load()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[date] = None,
        priority: Priority = Priority.MEDIUM,
    ) -> Task:
        """Agrega una nueva tarea a la agenda."""
        if not title.strip():
            raise ValueError("El título de la tarea no puede estar vacío.")
        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip(),
            due_date=due_date,
            priority=priority,
            status=Status.PENDING,
        )
        self._tasks.append(task)
        self._next_id += 1
        self._save()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retorna la tarea con el id indicado, o None si no existe."""
        return next((t for t in self._tasks if t.id == task_id), None)

    def list_pending(self) -> List[Task]:
        """Retorna todas las tareas con estado pendiente."""
        return [t for t in self._tasks if t.status == Status.PENDING]

    def list_all(self) -> List[Task]:
        """Retorna todas las tareas."""
        return list(self._tasks)

    def complete_task(self, task_id: int) -> Task:
        """Marca una tarea como completada."""
        task = self._get_or_raise(task_id)
        task.status = Status.DONE
        self._save()
        return task

    def delete_task(self, task_id: int) -> Task:
        """Elimina una tarea de la agenda."""
        task = self._get_or_raise(task_id)
        self._tasks.remove(task)
        self._save()
        return task

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        data = {
            "next_id": self._next_id,
            "tasks": [t.to_dict() for t in self._tasks],
        }
        self._storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _load(self) -> None:
        if not self._storage_path.exists():
            return
        data = json.loads(self._storage_path.read_text())
        self._next_id = data.get("next_id", 1)
        self._tasks = [Task.from_dict(t) for t in data.get("tasks", [])]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"No existe una tarea con id={task_id}.")
        return task
