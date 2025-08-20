__app_name__ = "pyjot"
__version__ = "0.1.0"


(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    DB_EXISTS_ERROR,
    JSON_ERROR,
    ID_ERROR,
) = range(8)

ERRORS = {
    DIR_ERROR: "error on accessing config directory",
    FILE_ERROR: "error on accessing config file",
    DB_READ_ERROR: "error on reading the database",
    DB_WRITE_ERROR: "error on writing to the database",
    DB_EXISTS_ERROR: "database already exists",
    JSON_ERROR: "error on accessing the database",
    ID_ERROR: "task ID not found",
}
