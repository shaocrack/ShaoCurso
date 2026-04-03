"""Punto de entrada de la agenda por línea de comandos."""

import argparse
from datetime import date

from .agenda import Agenda
from .models import Priority, Status


def _priority_label(p: Priority) -> str:
    icons = {Priority.LOW: "🟢", Priority.MEDIUM: "🟡", Priority.HIGH: "🔴"}
    return f"{icons[p]} {p.value}"


def _print_tasks(tasks):
    if not tasks:
        print("  (sin tareas)")
        return
    for task in tasks:
        due = task.due_date.isoformat() if task.due_date else "sin fecha"
        status_icon = "✅" if task.status == Status.DONE else "⏳"
        print(
            f"  [{task.id:>3}] {status_icon} {task.title} "
            f"| {_priority_label(task.priority)} "
            f"| vence: {due}"
        )
        if task.description:
            print(f"         → {task.description}")


def cmd_list(agenda: Agenda, args) -> None:
    tasks = agenda.list_all() if args.all else agenda.list_pending()
    title = "Todas las tareas" if args.all else "Tareas pendientes"
    print(f"\n📋  {title}")
    print("-" * 50)
    _print_tasks(tasks)
    print()


def cmd_add(agenda: Agenda, args) -> None:
    due = date.fromisoformat(args.due) if args.due else None
    priority = Priority(args.priority)
    task = agenda.add_task(
        title=args.title,
        description=args.description or "",
        due_date=due,
        priority=priority,
    )
    print(f"\n✅  Tarea #{task.id} agregada: '{task.title}'\n")


def cmd_complete(agenda: Agenda, args) -> None:
    task = agenda.complete_task(args.id)
    print(f"\n🎉  Tarea #{task.id} '{task.title}' marcada como completada.\n")


def cmd_delete(agenda: Agenda, args) -> None:
    task = agenda.delete_task(args.id)
    print(f"\n🗑️  Tarea #{task.id} '{task.title}' eliminada.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agenda",
        description="Sistema de agenda — gestiona tus tareas pendientes.",
    )
    parser.add_argument(
        "--storage",
        default="agenda_data.json",
        help="Archivo de almacenamiento (default: agenda_data.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("listar", help="Muestra las tareas pendientes.")
    p_list.add_argument("--all", action="store_true", help="Incluye tareas completadas.")
    p_list.set_defaults(func=cmd_list)

    # add
    p_add = subparsers.add_parser("agregar", help="Agrega una nueva tarea.")
    p_add.add_argument("title", help="Título de la tarea.")
    p_add.add_argument("-d", "--description", default="", help="Descripción.")
    p_add.add_argument(
        "--due", default=None, metavar="YYYY-MM-DD", help="Fecha de vencimiento."
    )
    p_add.add_argument(
        "--priority",
        choices=[p.value for p in Priority],
        default=Priority.MEDIUM.value,
        help="Prioridad (default: media).",
    )
    p_add.set_defaults(func=cmd_add)

    # complete
    p_complete = subparsers.add_parser("completar", help="Marca una tarea como completada.")
    p_complete.add_argument("id", type=int, help="ID de la tarea.")
    p_complete.set_defaults(func=cmd_complete)

    # delete
    p_delete = subparsers.add_parser("eliminar", help="Elimina una tarea.")
    p_delete.add_argument("id", type=int, help="ID de la tarea.")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    agenda = Agenda(storage_path=args.storage)
    args.func(agenda, args)


if __name__ == "__main__":
    main()
