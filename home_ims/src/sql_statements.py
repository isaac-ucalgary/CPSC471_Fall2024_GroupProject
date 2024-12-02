import json
import os
import copy

# Do we need abspath here? -Daniel
STATEMENTS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "sql_statements.json"))
INDENT_SPACES = 2

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


    def __str__(self) -> str:

        def make_title(title:str) -> str:
            title = title.replace("\n", "")
            title_middle = f"--- {title} ---" 
            title_middle_length = len(title_middle)
            full_title = ("-" * title_middle_length + "\n" +
                          title_middle + "\n" +
                          "-" * title_middle_length + "\n")
            return full_title

        def format_query(query:list[str]|str) -> str:
            formatted_query = ""

            if type(query) is list:
                indent_level = 0
                keyword = ""
                keyword_offset:dict[int,int] = { 0: 0 }
                new_keyword_offset:dict[int,int] = copy.deepcopy(keyword_offset)
                valid_keywords = ["SELECT", "FROM", "JOIN", "GROUP", "WHERE", "SET"]


                # Parse each line of the query
                for line in query:
                    # Check if this line starts by closing an indentation level
                    start_closing_bracket = (len(line.strip()) > 0 and line.strip()[0] == ')')
                    start_open_bracket = (len(line.strip()) > 0 and line.strip()[0] == '(')

                    new_indent_level = indent_level + line.count('(') - line.count(')')

                    # Get the keyword
                    if len(line.strip()) > 0:
                        keyword = line.strip(' \n\t()').split(" ")[0]

                    # Check if the keyword demands recomputing the offset at this level
                    if keyword in valid_keywords:
                        keyword_offset[indent_level + start_open_bracket] = 0 # Reset keyword_offset for this indent level
                        new_keyword_offset[indent_level + start_open_bracket] = len(keyword) + 1 # Set the new keyword_offset for future lines at this level

                    # Calculate the offset for the keyword for this offset level including all offsets at the lower levels
                    total_keyword_offset = 0
                    for level, offset in keyword_offset.items():
                        if level <= new_indent_level:
                            total_keyword_offset += offset

                    # Add line with correct indentation
                    formatted_query += (
                        " " * INDENT_SPACES * (indent_level - start_closing_bracket) + # Creates an indent for bracket groups 
                        " " * total_keyword_offset + # Creates an indent for keywords
                        line +
                        "\n"
                    )

                    # Calculate the new indent
                    indent_level = new_indent_level

                    # Record the new keyword_offset for future offsets
                    keyword_offset = copy.deepcopy(new_keyword_offset)

            else:
                formatted_query += str(query) + "\n"


            return formatted_query


        # Create string builder
        output_string = ""
        
        # --- Database Setup // DDL ---
        output_string += make_title(make_title("Database Setup // DDL"))

        output_string += "\n" * 1

        # ddl queries
        for function in self._sql_functions["ddl"]:
            function:dict
            query:list[str]|str = function["query"]

            output_string += format_query(query)
            output_string += "\n"

        output_string += "\n" * 3


        # --- DML/DQL ---
        output_string += make_title(make_title("Database Queries // DML/DQL"))

        output_string += "\n" * 2

        # dml/dql queries
        for table_name, table_functions in self._sql_functions["dml/dql"].items():
            table_name:str
            table_functions:dict[str, dict]

            # Generate the title for this group of functions
            output_string += make_title(table_name)

            # Generate each function
            for name, function in table_functions.items():
                name:str
                function:dict
                query:list[str]|str = function["query"]

                output_string += f"-- {name} --\n"
                output_string += format_query(query)

                output_string += "\n"

            output_string += "\n"


        return output_string.strip()



    def _load(self) -> None:
        """
        Used to load all the sql statements from the json file.
        """

        # Load all the sql statements from the json file
        with open(STATEMENTS_FILE, "r") as file:
            self._sql_functions = json.load(file)

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

        ddl_functions:list[dict] = copy.deepcopy(self._sql_functions["ddl"])

        # Join multiline strings
        for function in ddl_functions:
            function:dict
            query:list[str]|str = function["query"]

            if type(query) is list:
                function["query"] = " ".join(query)

        # Sort by execution order
        ddl_functions.sort(key= lambda x: x["order"])

        return ddl_functions



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

        sql_functions:dict[str, dict[str, dict]] = copy.deepcopy(self._sql_functions["dml/dql"])

        # Join multiline queries
        for table_functions in sql_functions.values():
            table_functions:dict[str, dict]

            for function in table_functions.values():
                function:dict
                query:list[str]|str = function["query"]

                if type(query) is list:
                    function["query"] = " ".join(query)

        return sql_functions



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
        return " ".join(self._sql_functions["dml/dql"][group][name]["query"])



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
        return copy.deepcopy(self._sql_functions["dml/dql"][group][name]["outputs"])

