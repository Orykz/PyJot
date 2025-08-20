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
WARNING_ALERT = "italic #F9FF85"


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


@app.command(name="complete")
def set_complete(todo_id: int = typer.Argument(...)) -> None:
    todoer = _get_todoer()
    todo, error = todoer.set_complete(todo_id)

    if error:
        console.print(
            f"Cannot switch completion for task #{todo_id}: {ERRORS[error]}",
            style=ERROR_ALERT,
            highlight=False,
        )
        raise typer.Exit(1)

    console.print(
        f"Task #{todo_id} completion has been switched to [bold]{todo['Complete']}[/bold]",
        style=SUCCESS_ALERT,
        highlight=False,
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
            console.print(
                f"Removing task failed: {ERRORS[error]}",
                style=ERROR_ALERT,
                highlight=False,
            )
            raise typer.Exit(1)
        else:
            console.print(
                f"Task #{todo_id}: {todo['Task']} was removed",
                style=SUCCESS_ALERT,
                highlight=False,
            )

    if force:
        _remove()
    else:
        todo_list = todoer.get_todo_list()

        try:
            todo = todo_list[todo_id - 1]
        except IndexError:
            console.print(
                f"Task #{todo_id} is invalid",
                style=ERROR_ALERT,
                highlight=False,
            )
            raise typer.Exit(1)

        delete = typer.confirm(f"Delete task #{todo_id}: {todo['Task']}?")
        if delete:
            _remove()
        else:
            console.print(
                "Operation was canceled",
                style=WARNING_ALERT,
                highlight=False,
            )


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
            console.print(
                f"Removing tasks failed: {ERRORS[error]}",
                style=ERROR_ALERT,
                highlight=False,
            )
            raise typer.Exit(1)
        else:
            console.print(
                "All tasks were removed",
                style=SUCCESS_ALERT,
                highlight=False,
            )
    else:
        console.print(
            "Operation was canceled",
            style=WARNING_ALERT,
            highlight=False,
        )


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
