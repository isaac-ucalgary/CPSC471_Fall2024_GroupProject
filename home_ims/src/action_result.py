from mysql.connector.types import RowType
from typing import Any

class ActionResult:
    """
    A simple object to standardise what a database action will return.
    """

    def __init__(self, success:bool=True, data:list[dict[str, Any]]|str|None=None, error_message:str|None=None, exception:Exception|None=None, warnings:list|None=None) -> None:
        self.error_occurred:bool = not error_message is None or not exception is None
        self.success:bool = success and not self.error_occurred

        # If the data is either an empty string or only consists of blank characters then there is no data
        if type(data) is str and not data.strip():
            data = None
        elif type(data) is list and len(data) == 0:
            data = None

        if type(warnings) is list and len(warnings) == 0:
            warnings = None

        self.warnings:list|None = warnings

        self.data:list[dict[str,Any]]|str|None = data

        self.error_message:str|None = error_message

        self.exception:Exception|None = exception


    def get_data(self) -> list[dict[str,Any]]|str|None:
        return self.data

    def get_data_list(self) -> list[dict[str,Any]]:
        if type(self.data) is list:
            return self.data
        else:
            return []


    def get_error_message(self) -> str|None:
        return self.error_message

    def is_success(self) -> bool:
        return self.success

    def is_error(self) -> bool:
        return self.error_occurred

    def get_exception(self) -> Exception|None:
        return self.exception

    def get_warnings(self) -> list|None:
        return self.warnings
