import typer

from typing import Optional, List
from pathlib import Path

from pyjot import __app_name__, __version__, ERRORS, config, database, pyjot

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        f"default: {str(database.DEFAULT_DB_FILE_PATH)}",
        "--db-path",
        "-db",
        prompt="location to create database",
    ),
) -> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f"Cannot create config file: {ERRORS[app_init_error]}", fg=typer.colors.RED
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f"Cannot create database: {ERRORS[db_init_error]}", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The database is located on {db_path}", fg=typer.colors.GREEN)


@app.command()
def add(
    task: List[str] = typer.Argument(...),
    priority: int = typer.Option(2, "--priority", "-p", min=1, max=4),
) -> None:
    todoer = _get_todoer()
    todo, error = todoer.add(task, priority)
    if error:
        typer.secho(f"Adding task failed: {ERRORS[error]}", fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(
            f"task added: '{todo['Description']}' (priority: {priority})",
            fg=typer.colors.GREEN,
        )


def _get_todoer() -> pyjot.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please run "pyjot init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if db_path.exists():
        return pyjot.Todoer(db_path)
    else:
        typer.secho(
            'Database not found. Please run "pyjot init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
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
