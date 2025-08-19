from configparser import ConfigParser
from pathlib import Path

from pyjot import DB_EXISTS_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "_todo.json")


def get_database_path(config_file: Path) -> Path:
    config_parser = ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    try:
        db_path.write_text("[]")  # empty to-do list
        return SUCCESS
    except OSError:
        return DB_EXISTS_ERROR
