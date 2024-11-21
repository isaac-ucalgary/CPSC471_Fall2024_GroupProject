import json
import os

STATEMENTS_FILE = os.path.abspath(os.path.dirname(__file__) + "/sql_statements.json")

def get_ddl_sql_functions() -> list[dict[str, str|int|list[str]|list[int]]]:
    """
    Gets the ddl sql functions from the json file.
    Assumes the json file is in the same directory as this script.
    The ddl sql functions will be returned sorted in the order they 
    should be ran in in order to create the database.

    Returns
    -------
    list[dict[str, str|int|list[str]|list[int]]]:
        The list of ddl sql functions.
    """

    ddl_sql_functions:list[dict]

    # Get the ddl functions from the json file
    with open(STATEMENTS_FILE, "r") as file:
        ddl_sql_functions = json.load(file)["ddl"]

    # json does not support multiline strings so convert the list of strings into a single string
    for function in ddl_sql_functions:
        function:dict
        query:list[str]|str = function["query"]

        if type(query) is list:
            function["query"] = " ".join(query)

    # Sort the functions by the order they are intended to be ran in
    ddl_sql_functions.sort(key= lambda x: x["order"])

    return ddl_sql_functions



def get_dmldql_sql_functions() -> dict[str, dict[str, dict[str, str|int|list[str]|list[int]]]]:
    """
    Gets the dml/dql sql functions from the json file.
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

    sql_functions:dict[str, dict[str, dict]]

    # Get the ddl functions from the json file
    with open(STATEMENTS_FILE, "r") as file:
        sql_functions = json.load(file)["dml/dql"]

    # json does not support multiline strings so convert queries from a list of strings into single strings
    for table_functions in sql_functions.values():
        table_functions:dict[str, dict]

        for function in table_functions.values():
            function:dict
            query:list[str]|str = function["query"]

            if type(query) is list:
                function["query"] = " ".join(query)

    return sql_functions



def get_query(group:str, name:str) -> str:
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

    sql_functions:dict[str, dict[str, dict]]

    # Get the ddl functions from the json file
    with open(STATEMENTS_FILE, "r") as file:
        sql_functions = json.load(file)["dml/dql"]

    return " ".join(sql_functions[group][name]["query"])



def get_query_inputs(group:str, name:str) -> list[str]:
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

    sql_functions:dict[str, dict[str, dict]]

    # Get the ddl functions from the json file
    with open(STATEMENTS_FILE, "r") as file:
        sql_functions = json.load(file)["dml/dql"]

    return sql_functions[group][name]["inputs"]



def get_query_outputs(group:str, name:str) -> list[str]:
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

    sql_functions:dict[str, dict[str, dict]]

    # Get the ddl functions from the json file
    with open(STATEMENTS_FILE, "r") as file:
        sql_functions = json.load(file)["dml/dql"]

    return sql_functions[group][name]["outputs"]

