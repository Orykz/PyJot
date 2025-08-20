import typer
from rich import box
from rich.console import Console
from rich.table import Table

from typing import Optional, List, Dict
from pathlib import Path

from pyjot import __app_name__, __version__, ERRORS, config, database, pyjot

app = typer.Typer()
console = Console()

_COLORS: Dict[str, str] = {
    "active": "#00D9FF",
    "inactive": "#006475",
}

_ALERTS: Dict[str, str] = {
    "success": "italic #59FF5F",
    "warning": "italic #F9FF85",
    "error": "bold #FF5959",
}


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="select location to create database. default: ",
    ),
) -> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        _print_console(
            f"Cannot create config file: {ERRORS[app_init_error]}",
            _ALERTS["error"],
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        _print_console(
            f"Cannot create database: {ERRORS[db_init_error]}",
            _ALERTS["error"],
        )
        raise typer.Exit(1)
    else:
        _print_console(
            f"The database is located on {db_path}",
            _ALERTS["success"],
        )


@app.command()
def add(
    task: List[str] = typer.Argument(...),
    priority: int = typer.Option(2, "--priority", "-p", min=1, max=4),
) -> None:
    todoer = _get_todoer()
    todo, error = todoer.add(task, priority)
    if error:
        _print_console(
            f"Adding task failed: {ERRORS[error]}",
            _ALERTS["error"],
        )
        raise typer.Exit(1)
    else:
        _print_console(
            f"task added: '{todo['Task']}' (priority: {priority})",
            _ALERTS["success"],
        )


@app.command(name="list")
def list_all() -> None:
    todoer = _get_todoer()
    todo_list = todoer.get_todo_list()
    if not todo_list:
        _print_console(
            "No existing tasks. Use the command '[italic]pyjot add <task>[/italic]'",
            _ALERTS["error"],
        )
        raise typer.Exit()

    table = Table(
        title="To-Do List",
        border_style=_COLORS["inactive"],
        title_style=f"bold italic {_COLORS['active']}",
        header_style=f"bold {_COLORS['active']}",
        box=box.ASCII,
    )
    table.add_column("ID")
    table.add_column("Priority")
    table.add_column("Completed")
    table.add_column("Task")
    for id, todo in enumerate(todo_list, start=1):
        task, prio, complete = todo.values()
        text_color = _COLORS["inactive"] if complete else _COLORS["active"]
        table.add_row(str(id), str(prio), str(complete), task, style=text_color)

    console.print(table)


@app.command(name="complete")
def set_complete(todo_id: int = typer.Argument(...)) -> None:
    todoer = _get_todoer()
    todo, error = todoer.set_complete(todo_id)

    if error:
        _print_console(
            f"Failed to switch completion for task #{todo_id}: {ERRORS[error]}",
            _ALERTS["error"],
        )
        raise typer.Exit(1)

    _print_console(
        f"Task #{todo_id} completion was switched to [bold]{todo['Complete']}[/bold]",
        _ALERTS["success"],
    )


@app.command()
def remove(
    todo_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force the deletion of task without confirming.",
    ),
) -> None:
    todoer = _get_todoer()

    def _remove():
        todo, error = todoer.remove(todo_id)
        if error:
            _print_console(f"Removing task failed: {ERRORS[error]}", _ALERTS["error"])
            raise typer.Exit(1)
        else:
            _print_console(
                f"Task #{todo_id}: {todo['Task']} was removed", _ALERTS["success"]
            )

    if force:
        _remove()
    else:
        todo_list = todoer.get_todo_list()

        try:
            todo = todo_list[todo_id - 1]
        except IndexError:
            _print_console(f"Task #{todo_id} is invalid", _ALERTS["error"])
            raise typer.Exit(1)

        delete = typer.confirm(f"Delete task #{todo_id}: {todo['Task']}?")
        if delete:
            _remove()
        else:
            _print_console("Operation was canceled", _ALERTS["warning"])


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all tasks?",
        help="Force the deletion of tasks without confirming.",
    ),
) -> None:
    todoer = _get_todoer()

    if force:
        error = todoer.remove_all().error
        if error:
            _print_console(f"Removing tasks failed: {ERRORS[error]}", _ALERTS["error"])
            raise typer.Exit(1)
        else:
            _print_console("All tasks were removed", _ALERTS["success"])
    else:
        _print_console("Operation was canceled", _ALERTS["warning"])


def _get_todoer() -> pyjot.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        _print_console(
            "Config file not found. Please run '[italic]pyjot init[/italic]'",
            _ALERTS["error"],
        )
        raise typer.Exit(1)

    if db_path.exists():
        return pyjot.Todoer(db_path)
    else:
        _print_console(
            "Database not found. Please run '[italic]pyjot init[/italic]'",
            _ALERTS["error"],
        )
        raise typer.Exit(1)


def _print_console(text: str, alert: str):
    console.print(text, style=alert, highlight=False)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return
