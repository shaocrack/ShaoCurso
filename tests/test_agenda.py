import json
import tempfile
from datetime import date
from pathlib import Path

import pytest

from agenda import Agenda, Priority, Status


@pytest.fixture
def tmp_agenda(tmp_path):
    """Agenda respaldada en un archivo temporal."""
    return Agenda(storage_path=str(tmp_path / "test_data.json"))


# ------------------------------------------------------------------
# Agregar tareas
# ------------------------------------------------------------------

def test_add_task_returns_task(tmp_agenda):
    task = tmp_agenda.add_task("Comprar leche")
    assert task.id == 1
    assert task.title == "Comprar leche"
    assert task.status == Status.PENDING


def test_add_task_with_all_fields(tmp_agenda):
    task = tmp_agenda.add_task(
        title="Estudiar Python",
        description="Capítulo 5",
        due_date=date(2026, 12, 31),
        priority=Priority.HIGH,
    )
    assert task.description == "Capítulo 5"
    assert task.due_date == date(2026, 12, 31)
    assert task.priority == Priority.HIGH


def test_add_task_empty_title_raises(tmp_agenda):
    with pytest.raises(ValueError):
        tmp_agenda.add_task("   ")


def test_add_multiple_tasks_increments_id(tmp_agenda):
    t1 = tmp_agenda.add_task("Tarea 1")
    t2 = tmp_agenda.add_task("Tarea 2")
    assert t2.id == t1.id + 1


# ------------------------------------------------------------------
# Listar pendientes
# ------------------------------------------------------------------

def test_list_pending_only_returns_pending(tmp_agenda):
    tmp_agenda.add_task("Tarea A")
    tmp_agenda.add_task("Tarea B")
    tmp_agenda.complete_task(1)

    pending = tmp_agenda.list_pending()
    assert len(pending) == 1
    assert pending[0].title == "Tarea B"


def test_list_pending_empty_when_all_done(tmp_agenda):
    tmp_agenda.add_task("Solo una")
    tmp_agenda.complete_task(1)
    assert tmp_agenda.list_pending() == []


# ------------------------------------------------------------------
# Completar tarea
# ------------------------------------------------------------------

def test_complete_task_changes_status(tmp_agenda):
    tmp_agenda.add_task("Limpiar la casa")
    task = tmp_agenda.complete_task(1)
    assert task.status == Status.DONE


def test_complete_nonexistent_task_raises(tmp_agenda):
    with pytest.raises(KeyError):
        tmp_agenda.complete_task(999)


# ------------------------------------------------------------------
# Eliminar tarea
# ------------------------------------------------------------------

def test_delete_task_removes_it(tmp_agenda):
    tmp_agenda.add_task("Tarea temporal")
    tmp_agenda.delete_task(1)
    assert tmp_agenda.get_task(1) is None
    assert tmp_agenda.list_all() == []


def test_delete_nonexistent_task_raises(tmp_agenda):
    with pytest.raises(KeyError):
        tmp_agenda.delete_task(42)


# ------------------------------------------------------------------
# Persistencia
# ------------------------------------------------------------------

def test_persistence_across_instances(tmp_path):
    storage = str(tmp_path / "shared.json")
    a1 = Agenda(storage_path=storage)
    a1.add_task("Persistir esto")

    a2 = Agenda(storage_path=storage)
    assert len(a2.list_all()) == 1
    assert a2.list_all()[0].title == "Persistir esto"


def test_persistence_preserves_status(tmp_path):
    storage = str(tmp_path / "shared.json")
    a1 = Agenda(storage_path=storage)
    a1.add_task("Completar y guardar")
    a1.complete_task(1)

    a2 = Agenda(storage_path=storage)
    assert a2.get_task(1).status == Status.DONE
    assert a2.list_pending() == []
