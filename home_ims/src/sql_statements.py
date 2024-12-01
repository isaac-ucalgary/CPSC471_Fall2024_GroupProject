import json
import os
import copy

STATEMENTS_FILE = os.path.abspath(os.path.dirname(__file__) + "/sql_statements.json")

class SQL_Statements:
    """
    A class containing all of the SQL statements for the project.

    Loads the SQL statements from the `sql_statements.json` file located in the same
    directory as this class file and then references that loaded dictionary for all
    requests for SQL statements.

    The dictionary of SQL statements can be reloaded from the same json file using 
    `<myobj>.reload()`.
    """

    def __init__(self):

        self._sql_functions = {}

        self._load()


    def _load(self) -> None:
        """
        Used to load all the sql statements from the json file.
        """

        # Load all the sql statements from the json file
        with open(STATEMENTS_FILE, "r") as file:
            self._sql_functions = json.load(file)

        # -- Convert multiline strings (lists of strings) into single strings --
        # ddl functions
        for function in self._sql_functions["ddl"]:
            function:dict
            query:list[str]|str = function["query"]

            if type(query) is list:
                function["query"] = " ".join(query)

        # other dml/dql functions
        for table_functions in self._sql_functions["dml/dql"].values():
            table_functions:dict[str, dict]

            for function in table_functions.values():
                function:dict
                query:list[str]|str = function["query"]

                if type(query) is list:
                    function["query"] = " ".join(query)


        # Sort ddl functions to be the in the order of intended execution
        self._sql_functions["ddl"].sort(key= lambda x: x["order"])

        

    def reload(self) -> None:
        """
        Reloads all the sql statements from the json file.
        """
        self._load()






    def get_ddl_sql_functions(self) -> list[dict[str, str|int|list[str]|list[int]]]:
        """
        Gets the ddl sql functions from the preloaded json file.
        The ddl sql functions will be returned sorted in the order they 
        should be ran in in order to create the database.

        Returns
        -------
        list[dict[str, str|int|list[str]|list[int]]]:
            The list of ddl sql functions.
        """

        # ddl_sql_functions:list[dict] = self._sql_functions["ddl"]
        #
        # # # Get the ddl functions from the json file
        # # with open(STATEMENTS_FILE, "r") as file:
        # #     ddl_sql_functions = json.load(file)["ddl"]
        #
        # # json does not support multiline strings so convert the list of strings into a single string
        # # for function in ddl_sql_functions:
        # #     function:dict
        # #     query:list[str]|str = function["query"]
        # #
        # #     if type(query) is list:
        # #         function["query"] = " ".join(query)
        #
        # # Sort the functions by the order they are intended to be ran in
        # ddl_sql_functions.sort(key= lambda x: x["order"])
        #
        # return ddl_sql_functions

        # return [x for x in self._sql_functions["ddl"].sort(key= lambda x: x["order"])]
        return copy.deepcopy(self._sql_functions["ddl"].sort(key= lambda x: x["order"]))



    def get_dmldql_sql_functions(self) -> dict[str, dict[str, dict[str, str|int|list[str]|list[int]]]]:
        """
        Gets the dml/dql sql functions from the preloaded json file.
        Assumes the json file is in the same directory as this script.

        Returns
        -------
        dict[str, list[dict[str, str|int|list[str]|list[int]]]]
            The dictionary of dml/dql sql functions.

            The key is the name of a table or context group.

            The value is a list of function of which their statements act
            upon the table of the same name as the key, or their function 
            is most similar to the others in the rest of the group for 
            that table.
            Said list is a list of dictionaries of functions.
        """

        # sql_functions:dict[str, dict[str, dict]] = self._sql_functions["dml/dql"]

        # # Get the ddl functions from the json file
        # with open(STATEMENTS_FILE, "r") as file:
        #     sql_functions = json.load(file)["dml/dql"]
        #
        # # json does not support multiline strings so convert queries from a list of strings into single strings
        # for table_functions in sql_functions.values():
        #     table_functions:dict[str, dict]
        #
        #     for function in table_functions.values():
        #         function:dict
        #         query:list[str]|str = function["query"]
        #
        #         if type(query) is list:
        #             function["query"] = " ".join(query)
        #
        # return sql_functions

        return copy.deepcopy(self._sql_functions["dml/dql"])



    def get_query(self, group:str, name:str) -> str:
        """
        Gets a dml/dql query for a sql function called `name` in the 
        group (or table category) called `group`.

        Parameters
        ----------
        group : `str`
            The group or table category to get the function from.
        name : `str`
            The name of the function to get the query of.

        Returns
        -------
        str
            The query of the desired function.
        """

        # sql_functions:dict[str, dict[str, dict]]
        #
        # # Get the ddl functions from the json file
        # with open(STATEMENTS_FILE, "r") as file:
        #     sql_functions = json.load(file)["dml/dql"]
        #
        # return " ".join(sql_functions[group][name]["query"])

        return self._sql_functions["dml/dql"][group][name]["query"]



    def get_query_inputs(self, group:str, name:str) -> list[str]:
        """
        Gets the inputs for a dml/dql query for a sql function called `name` in the 
        group (or table category) called `group`.

        Parameters
        ----------
        group : `str`
            The group or table category to get the function from.
        name : `str`
            The name of the function query to get inputs of.

        Returns
        -------
        list[str]
            The inputs for the query of the desired function.
        """

        # sql_functions:dict[str, dict[str, dict]]
        #
        # # Get the ddl functions from the json file
        # with open(STATEMENTS_FILE, "r") as file:
        #     sql_functions = json.load(file)["dml/dql"]
        #
        # return sql_functions[group][name]["inputs"]

        # return [x for x in self._sql_functions["dml/dql"][group][name]["inputs"]]
        return copy.deepcopy(self._sql_functions["dml/dql"][group][name]["inputs"])



    def get_query_outputs(self, group:str, name:str) -> list[str]:
        """
        Gets the outputs for a dml/dql query for a sql function called `name` in the 
        group (or table category) called `group`.

        Parameters
        ----------
        group : `str`
            The group or table category to get the function from.
        name : `str`
            The name of the function to get the query of.

        Returns
        -------
        list[str]
            The outputs for the query of the desired function.
        """

        # sql_functions:dict[str, dict[str, dict]]
        #
        # # Get the ddl functions from the json file
        # with open(STATEMENTS_FILE, "r") as file:
        #     sql_functions = json.load(file)["dml/dql"]
        #
        # return sql_functions[group][name]["outputs"]

        # return [x for x in self._sql_functions["dml/dql"][group][name]["outputs"]]
        return copy.deepcopy(self._sql_functions["dml/dql"][group][name]["outputs"])

