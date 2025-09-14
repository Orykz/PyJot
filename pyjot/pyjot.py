from typing import Dict, Any, NamedTuple, List
from pathlib import Path

from pyjot import ID_ERROR
from pyjot.database import DatabaseHandler


class TodoResult(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    """Manages all the todo task transactions.

    Attributes:
        _db_handler (DatabaseHandler): The DatabaseHandler class.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, task: List[str], priority: int = 2) -> TodoResult:
        """Add the task to the todo list.

        Args:
            task (List[str]): The task to add.
            priority (int, default 2): priority value.

        Returns:
            TodoResult: NamedTuple of (todo task, error code).
        """
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
        """Gets the todo list from the database.

        Returns:
            List[Dict[str, Any]]: the todo list.
        """
        read = self._db_handler.read_todos()
        return read.todo_list

    def set_complete(self, todo_id: int) -> TodoResult:
        """Switch the completion boolean value of the todo task (sets to True and vice versa).

        Args:
            todo_id (int): The todo task id.

        Returns:
            TodoResult: NamedTuple of (todo task, error code).

        Raises:
            IndexError: if the todo task id does not exist.
        """
        read = self._db_handler.read_todos()
        if read.error:
            return TodoResult({}, read.error)

        try:
            todo = read.todo_list[todo_id - 1]
        except IndexError:
            return TodoResult({}, ID_ERROR)

        todo["Complete"] = not todo["Complete"]
        write = self._db_handler.write_todos(read.todo_list)
        return TodoResult(todo, write.error)

    def remove(self, todo_id: int) -> TodoResult:
        """Remove the todo task from the todo list.

        Args:
            todo_id (int): The todo task id.

        Returns:
            TodoResult: NamedTuple of (todo task, error code).

        Raises:
            IndexError: if the todo task id does not exist.
        """
        read = self._db_handler.read_todos()
        if read.error:
            return TodoResult({}, read.error)

        try:
            todo = read.todo_list.pop(todo_id - 1)
        except IndexError:
            return TodoResult({}, ID_ERROR)

        write = self._db_handler.write_todos(read.todo_list)
        return TodoResult(todo, write.error)

    def remove_all(self) -> TodoResult:
        """Empties the database.

        Returns:
            TodoResult: NamedTuple of (todo task, error code).
        """
        write = self._db_handler.write_todos([])
        return TodoResult({}, write.error)
