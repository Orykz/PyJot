import typer
from rich import box
from rich.console import Console
from rich.table import Table

from typing import Optional, List
from pathlib import Path

from pyjot import __app_name__, __version__, ERRORS, config, database, pyjot

app = typer.Typer()
console = Console()


ACTIVE_COLOR = "#00D9FF"
INACTIVE_COLOR = "#006475"
ERROR_ALERT = "bold #FF5959"
SUCCESS_ALERT = "italic #59FF5F"


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
        console.print(
            f"Cannot create config file: {ERRORS[app_init_error]}",
            style=ERROR_ALERT,
            highlight=False,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        console.print(
            f"Cannot create database: {ERRORS[db_init_error]}",
            style=ERROR_ALERT,
            highlight=False,
        )
        raise typer.Exit(1)
    else:
        console.print(
            f"The database is located on {db_path}",
            style=SUCCESS_ALERT,
            highlight=False,
        )


@app.command()
def add(
    task: List[str] = typer.Argument(...),
    priority: int = typer.Option(2, "--priority", "-p", min=1, max=4),
) -> None:
    todoer = _get_todoer()
    todo, error = todoer.add(task, priority)
    if error:
        console.print(
            f"Adding task failed: {ERRORS[error]}",
            style=ERROR_ALERT,
            highlight=False,
        )
        raise typer.Exit(1)
    else:
        console.print(
            f"task added: '{todo['Task']}' (priority: {priority})",
            style=SUCCESS_ALERT,
            highlight=False,
        )


@app.command(name="list")
def list_all() -> None:
    todoer = _get_todoer()
    todo_list = todoer.get_todo_list()
    if not todo_list:
        console.print(
            "No existing tasks. Use the command '[italic]pyjot add <task>[/italic]'",
            style=ERROR_ALERT,
            highlight=False,
        )
        raise typer.Exit()

    table = Table(
        title="To-Do List",
        border_style=INACTIVE_COLOR,
        title_style=f"bold italic {ACTIVE_COLOR}",
        header_style=f"bold {ACTIVE_COLOR}",
        box=box.ASCII,
    )
    table.add_column("ID")
    table.add_column("Priority")
    table.add_column("Completed")
    table.add_column("Task")
    for id, todo in enumerate(todo_list, start=1):
        task, prio, complete = todo.values()
        text_color = INACTIVE_COLOR if complete else ACTIVE_COLOR
        table.add_row(str(id), str(prio), str(complete), task, style=text_color)

    console.print(table)


def _get_todoer() -> pyjot.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        console.print(
            "Config file not found. Please run '[italic]pyjot init[/italic]'",
            style=ERROR_ALERT,
        )
        raise typer.Exit(1)

    if db_path.exists():
        return pyjot.Todoer(db_path)
    else:
        console.print(
            "Database not found. Please run '[italic]pyjot init[/italic]'",
            style=ERROR_ALERT,
        )
        raise typer.Exit(1)


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
