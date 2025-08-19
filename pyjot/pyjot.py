from typing import Dict, Any, NamedTuple, List
from pathlib import Path
from pyjot.database import DatabaseHandler


class CurrentTodo(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, task: List[str], priority: int = 2) -> CurrentTodo:
        task_text = " ".join(task)
        todo = {
            "Task": task_text,
            "Priority": priority,
            "Complete": False,
        }
        read = self._db_handler.read_todos()
        if read.error:
            return CurrentTodo(todo, read.error)

        read.todo_list.append(todo)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)
