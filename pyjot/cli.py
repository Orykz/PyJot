import typer

from typing import Optional
from pathlib import Path

from pyjot import __app_name__, __version__, ERRORS, config, database

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
