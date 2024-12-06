from mysql.connector.types import RowType



class Return_Formatted:
    """
    A simple object to standardise what a database action will return.
    """

    def __init__(self, success:bool=True, data:list[RowType]|str|None=None, error_message:str|None=None) -> None:
        self.error_occurred:bool = error_message is None
        self.success:bool = success and not self.error_occurred

        # If the data is either an empty string or only consists of blank characters then there is no data
        if type(data) is str and not data.strip():
            data = None


        self.data:list[RowType]|str|None = data
        self.error_message:str|None = error_message


    def get_data(self) -> list[RowType]|str|None:
        return self.data

    def get_error(self) -> str|None:
        return self.error_message

    def is_success(self) -> bool:
        return self.success

    def did_error_occur(self) -> bool:
        return self.error_occurred



