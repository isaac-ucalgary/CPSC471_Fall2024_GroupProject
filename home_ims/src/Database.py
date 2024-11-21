# Build Database Script

# -- Library Imports --
from os import stat
import re
from threading import ExceptHookArgs
import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.cursor import MySQLCursor
import inspect
from types import FunctionType, MethodType

# -- Local Imports --
from env import MARIADB_HOST, MARIADB_PORT, MARIADB_DATABASE_NAME, MARIADB_USER
from secrets import MARIADB_PASSWORD # (ignore error, it's caused by .gitignore file and is expected.)
from sql_statements import *



class Database:


    def __init__(self,
                 db_host:str=MARIADB_HOST,
                 db_port:int=MARIADB_PORT,
                 db_user:str=MARIADB_USER,
                 db_password:str=MARIADB_PASSWORD,
                 db_name:str=MARIADB_DATABASE_NAME
                 ):

        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        self.__connection = None
        self.__cursor = None

        self.db_actions = self.DB_Actions(self)




    # Connect to database
    # Creates a connection and a cursor
    def connect(self) -> bool:

        # Used to record the status of the operation.
        connection_success:bool = True

        # Try to connect to the database.
        try:
            self.__connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                collation="utf8mb4_unicode_ci"
            )

        except Error as e:
            print("Could not connect to database by name, trying to connect without one...")

            try:
                self.__connection = mysql.connector.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password,
                    collation="utf8mb4_unicode_ci"
                )

            except Error as e:
                print("Failed to connect to database")
                print(e)
                self.__connection = None
                connection_success = False
            else:
                print("Connected to MariaDB.")

                # Make the cursor on the newly created connection.
                self.__cursor = self.__connection.cursor()


        # If no error is raised
        else:
            if self.db_name:
                print(f"Connected to \"{self.db_name}\".")
            else:
                print("Connected to MariaDB.")

            # Make the cursor on the newly created connection.
            self.__cursor = self.__connection.cursor()

        # Returns the status of connecting to the database.
        return connection_success


        

    def close_connection(self) -> None:
        """
        Closes cursor and connection to the database.
        """
        # Close cursor.
        if self.__cursor is not None:
            self.__cursor.close()

        # Close connection.
        if self.__connection is not None:
            self.__connection.close()

    def close(self) -> None:
        """
        Alias for `close_connection`.
        """
        self.close_connection()


    def commit(self) -> None:
        """
        Commits any pending changes to the database.
        """
        if self.__connection is not None:
            self.__connection.commit()


    # Execute an SQL statement on the connected database
    # NOTE I think this function would work for all SQL queries?
    # NOTE We may want this to be psydo public
    def __exec_sql(self, sql_statement) -> bool:

        # Nothing has failed yet
        operation_successful:bool = True

        if self.__cursor is not None:
            try:
                self.__cursor.execute(sql_statement)
            except Error as e:
                print(e)
                operation_successful = False # Record failure

        else:
            operation_successful = False # Record failure
            if self.__connection is None:
                print("Could not execute SQL statement. Connection and cursor not established.")
            else:
                print("Could not execute SQL statement. Connection not established.")


        # Return success status
        return operation_successful



    def build_database(self) -> bool:

        # Nothing has failed yet
        operation_successful:bool = True

        # Get the ddl sql statements to build the database
        ddl = [x for x in get_ddl_sql_functions()]

        # Connect to the database
        operation_successful = self.connect() and operation_successful

        # Create the database and tables.
        if self.__connection:

            # Loop through the SQL statements for creating tables
            for function in ddl:
                function_name = function["function"]
                statement = function["query"]

                # Execute the statement
                operation_successful = self.__exec_sql(statement) and operation_successful

                # Print statements for debugging
                if operation_successful:
                    print(f"Success: {function_name}") # TODO Implement proper logging using the logging library
                else:
                    print(f"An error occurred whilst creating {function_name}. Not executing further statements.")
                    break

        else:
            operation_successful = False
            print(f"Connection failed, database {self.db_name} not created.")

        # Close the connection to the database
        self.close_connection()

        # Return the status of building the database
        return operation_successful

    


    # ---------------------------- #
    # ----- DATABASE ACTIONS ----- #
    # ---------------------------- #

    class DB_Actions(object):

        def __init__(self, parent):

            self.__parent = parent

            if not type(self.__parent) == Database:
                raise TypeError("Parent of all DB_Actions instances must be an instance of Database")


            def pre_func() -> bool:
                """
                The function to run before all class methods.

                Returns
                -------
                bool
                    Whether the main function should still be run.
                """

                run_main_func:bool = True

                con = getattr(self.__parent, "_Database__connection", None)

                # Check if connection is None
                if con is None:
                    print("Connection is None")
                    run_main_func = run_main_func and False

                # Check if connection is active
                if con is not None and not con.is_connected():
                    print("Database is not connected")
                    run_main_func = run_main_func and False

                cur = getattr(self.__parent, "_Database__cursor", None)

                # Check if cursor is indeed a cursor
                if cur is None:
                    print("Database cursor is None")
                    run_main_func = run_main_func and False

                return run_main_func


            def post_func():
                """
                The function to run after all class methods.
                """
                pass

            def replace_func(name:str) -> None:
                """
                Replaces the function of name "name" with pre and post function functions.
                
                If the name is not a present attribute of self or is not a function then 
                this function will have no result and will continue silently.
                
                Parameters
                ----------
                name : str
                    The name of the function to replace in self.
                """

                # Get the function to replace from self
                old_func = getattr(self, name, None)

                # Check that the function exists and is indeed a function
                if old_func is not None and type(old_func) in (FunctionType, MethodType):

                    # Define the new function with pre and post functions
                    def new_func(*args, **kargs):
                        result = None
                        if pre_func():
                            result = old_func(*args, **kargs)
                        else:
                            print("Function aborted")
                        post_func()
                        return result

                    # Set the new wrapped function in place of the unwrapped function
                    setattr(self, name, new_func)


            # Get members of self (the newly created object)
            members = inspect.getmembers_static(self)

            # Loop through the members looking for non dunder methods
            for name, value in members:

                # Check that the member is a function and is non-dunder
                if (type(value) == FunctionType 
                        and not name.startswith("__")
                        and not name.endswith("__")
                        ):
                    replace_func(name) # Replace the function
            




        # ----- DYNAMIC -----

        def dynamic_query(self, group:str, function_name:str, **kargs) -> bool|list[tuple]:
            """
            Executes any dml or dql query from the json file.


            Parameters
            ----------
            `group` : str
                The group that the desired query is apart of.
            `function_name` : str
                The name of the sql function to execute.
            `**kargs`
                See below


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - `group` is a valid group.
            - `function_name` is a valid function name within the `group`.
            - All of the required inputs for the function are provided in `**kargs`.

            Keyword Arguments
            -----------------
            Set the keywords for the inputs defined for the sql function defined in
            the sql_statements.json file.

            Returns
            -------
            bool | list[tuple]
                If the statement is a `SELECT` query then the function returns a list 
                of tuples (`list[tuple]`). 
                Otherwise if the operation was successful returns `True`.
                If the operation fails for any reason (i.e. not all the required inputs
                that the function required were provided) then returns `False`.
            """

            # -- Get the query --
            query = None
            required_inputs = None
            expected_outputs = None
            try:
                query = get_query(group = group, name = function_name)
                required_inputs = get_query_inputs(group = group, name = function_name)
                expected_outputs = get_query_outputs(group = group, name = function_name)
            except KeyError:
                print("Failed to get query information")
                return False


            # -- Gather inputs from **kargs --
            inputs = []

            for key in required_inputs:
                if key not in kargs.keys():
                    return False
                else:
                    inputs.append(kargs[key])

            inputs = tuple(inputs)


            # -- Execute the SQL statement --
            cursor:MySQLCursor = self.__parent._Database__cursor
            cursor.execute(query, inputs)


            # -- Get outputs --
            if len(expected_outputs) > 0:
                return cursor.fetchall()
            else:
                return True






            







        # ----- ITEM TYPE -----

        def add_item_type(self, name:str, unit:str) -> None:
            """
            Adds an item type record to the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = get_query(group = "ItemType", name = "Add item type")
            data = (name, unit)

            cursor.execute(statement, data)


        def select_item_type(self, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects item type records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
                Example: "M%"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"
                Example: "%"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = get_query(group = "ItemType", name = "Select item type")
            data = (name, unit)

            cursor.execute(statement, data)

            return cursor.fetchall()
            

        def add_item_type_subclass(self, subclass_name:str, name:str, unit:str="") -> None:
            """
            Adds an item type subclass record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            # Get the cursor
            cursor:MySQLCursor = self.__parent._Database__cursor

            # Create the item type if it doesn't exist
            if len(self.select_item_type(name)) == 0:
                self.add_item_type(name=name, unit=unit)

            # Create the subclass type
            statement = get_query(group=subclass_name, name=f"Add {subclass_name.lower()} type")
            data = (name,)

            cursor.execute(statement, data)


        def select_item_type_subclass(self, subclass_name:str, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects records of an item type subclass from the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            # Get the cursor
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = get_query(group=subclass_name, name = f"Select {subclass_name.lower()} type")
            data = (name, unit) # Yes, the comma is necessary

            cursor.execute(statement, data)

            return cursor.fetchall()



        # ----- CONSUMABLE -----

        def add_consumable_type(self, name:str, unit:str="") -> None:
            """
            Adds a consumable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            self.add_item_type_subclass(
                subclass_name="Consumable", 
                name=name,
                unit=unit
            )

        def select_consumable_type(self, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects consumable type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self.select_item_type_subclass(
                subclass_name="Consumable",
                name=name,
                unit=unit
            )

        def add_consumable_type_subclass(self, subclass_name:str, name:str, unit:str="") -> None:
            """
            Adds a consumable type subclass record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            # Create the consumable type if it doesn't exist
            if len(self.select_consumable_type(name)) == 0:
                self.add_consumable_type(name=name, unit=unit)

            # Create the consumable subclass type
            self.add_item_type_subclass(
                subclass_name=subclass_name,
                name=name,
                unit=unit
            )



        # ----- DURABLE -----

        def add_durable_type(self, name:str, unit:str="") -> None:
            """
            Adds a durable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Hammer"
            unit : str
                The unit that the item quantity is measured in.
                Example: "" (What are you measuring hammers in?)

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            self.add_item_type_subclass(
                subclass_name="Durable", 
                name=name,
                unit=unit
            )

        def select_durable_type(self, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects durable type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self.select_item_type_subclass(
                subclass_name="Durable",
                name=name,
                unit=unit
            )



        # ----- FOOD -----

        def add_food_type(self, name:str, unit:str="") -> None:
            """
            Adds a food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            name : str
                The name of the food item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the food item to add does not already exist in the table.
            """
            self.add_consumable_type_subclass(
                subclass_name="Food", 
                name=name,
                unit=unit
            )

        def select_food_type(self, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects food type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self.select_item_type_subclass(
                subclass_name="Food",
                name=name,
                unit=unit
            )



        # ----- NOT FOOD -----

        def add_notfood_type(self, name:str, unit:str="") -> None:
            """
            Adds a not food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            name : str
                The name of the not item to add.
                Example: "TidePods"
            unit : str
                The unit that the item quantity is measured in.
                Example: "kg"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the not food item to add does not already exist in the table.
            """
            self.add_consumable_type_subclass(
                subclass_name="NotFood", 
                name=name,
                unit=unit
            )

        def select_notfood_type(self, name:str="%", unit:str="%") -> list[tuple]:
            """
            Selects not food type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to add.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self.select_item_type_subclass(
                subclass_name="NotFood",
                name=name,
                unit=unit
            )



