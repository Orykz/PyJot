from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, List, NamedTuple
import json

from pyjot import SUCCESS, DB_EXISTS_ERROR, JSON_ERROR, DB_READ_ERROR, DB_WRITE_ERROR

DEFAULT_DB_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "_todo.json")


def get_database_path(config_file: Path) -> Path:
    """Get the database path from config.

    Args:
        config_file (Path): Path variable describing the config location.

    Returns:
        Path: The database location.
    """
    config_parser = ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    """Initialize the database if it does not exist.

    Args:
        db_path (Path): Path variable describing the database location.

    Returns:
        int: the error code.

    Raises:
        OSError: if database already exists.
    """
    try:
        db_path.write_text("[]")  # empty to-do list
        return SUCCESS
    except OSError:
        return DB_EXISTS_ERROR


class DBResponse(NamedTuple):
    todo_list: List[Dict[str, Any]]
    error: int


class DatabaseHandler:
    """Handles all the database access.

    Attributes:
        _db_path (Path): Path variable describing the database location.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_todos(self) -> DBResponse:
        """Get all todos from the database.

        Returns:
            DBResponse: tuple of (todo list, error code).

        Raises:
            json.JSONDecodeError: if could not load the database.
        """
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:
                    return DBResponse([], JSON_ERROR)
        except OSError:
            return DBResponse([], DB_READ_ERROR)

    def write_todos(self, todo_list: List[Dict[str, Any]]) -> DBResponse:
        """Write the todo list to the database.

        Args:
            todo_list (List[Dict[str, Any]]): The todo list.

        Returns:
            DBResponse: tuple of (todo list, error code).

        Raises:
            OSError: if could not write to the database.
        """
        try:
            with self._db_path.open("w") as db:
                json.dump(todo_list, db, indent=4)
            return DBResponse(todo_list, SUCCESS)
        except OSError:
            return DBResponse([], DB_WRITE_ERROR)
