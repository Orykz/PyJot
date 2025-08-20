from typing import Dict, Any, NamedTuple, List
from pathlib import Path
from pyjot.database import DatabaseHandler


class TodoResult(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, task: List[str], priority: int = 2) -> TodoResult:
        task_text = " ".join(task)
        todo = {
            "Task": task_text,
            "Priority": priority,
            "Complete": False,
        }
        read = self._db_handler.read_todos()
        if read.error:
            return TodoResult(todo, read.error)

        read.todo_list.append(todo)
        write = self._db_handler.write_todos(read.todo_list)
        return TodoResult(todo, write.error)

    def get_todo_list(self) -> List[Dict[str, Any]]:
        read = self._db_handler.read_todos()
        return read.todo_list
