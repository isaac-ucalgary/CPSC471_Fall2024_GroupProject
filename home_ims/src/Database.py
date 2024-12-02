# Build Database Script

# -- Library Imports --
from math import e
from time import time
from mysql.connector import Error, IntegrityError, MySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import RowType
from os import stat, times
from types import FunctionType, MethodType
import inspect
import mysql.connector
import re
import datetime as dt

# -- Local Imports --
from env import MARIADB_HOST, MARIADB_PORT, MARIADB_DATABASE_NAME, MARIADB_USER
from secrets import MARIADB_PASSWORD # (ignore error, it's caused by .gitignore file and is expected.)
from sql_statements import SQL_Statements



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

        self.__sql_statements = SQL_Statements()




    # Connect to database
    # Creates a connection and a cursor
    def connect(self) -> bool:

        # Try to connect to the database.
        try:
            self.__connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                collation="utf8mb4_unicode_ci",
                autocommit=True,
                get_warnings=True
            )

        except Error as e:
            print("Failed to connect to database")
            print(e)
            self.__connection = None
            return False
        else:
            print("Connected to MariaDB.")

            # Make the cursor on the newly created connection.
            self.__cursor = self.__connection.cursor(dictionary = True)
            return True
        

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

    def start_transaction(self) -> None:
        """
        Begins a database transaction.
        """
        if self.__connection is not None:
            self.__connection.start_transaction()

    def commit(self) -> None:
        """
        Commits any pending changes to the database.
        """
        if self.__connection is not None:
            self.__connection.commit()

    def rollback(self) -> None:
        """
        Rolls back any pending changes to the database.
        """
        if self.__connection is not None:
            self.__connection.rollback()


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
        connected_at_start = True

        # Get the ddl sql statements to build the database
        ddl = self.__sql_statements.get_ddl_sql_functions()

        # Connect to the database
        if not self.__connection:
            operation_successful = self.connect() and operation_successful
            connected_at_start = False

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
        if not connected_at_start:
            self.close_connection()

        # Return the status of building the database
        return operation_successful


    def build_demo_database(self) -> None:
        print("This will DROP the whole database and create the database from new and populate it with demo data.")
        print("\033[91mALL DATA WILL BE LOST\033[0m")
        accept_message = "RESET TO DEMO"
        user_input = input(f"To continue input \"{accept_message}\":")
        if user_input != accept_message:
            return None

        if self.connect() and self.__cursor is not None:

            # DROP DATABASE
            self.__cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name};")

            # Build the new database
            self.build_database()


            foods = [
                {"name":"Banana", "unit":""},
                {"name":"Potato", "unit":""},
                {"name":"Soup", "unit":"L"},
                {"name":"Milk", "unit":"L"},
                {"name":"Squash", "unit":""},
                {"name":"Spaghetti", "unit":"g"},
                {"name":"Pumpkin", "unit":"g"},
                {"name":"Ground Beef", "unit":"g"},
                {"name":"Goldfish", "unit":"g"},
                {"name":"Watermellon", "unit":""},
                {"name":"Cheddar", "unit":"g"},
                {"name":"Salmon", "unit":"g"},
                {"name":"Haggis", "unit":"kg"},
                {"name":"Rice", "unit":"g"},
                {"name":"Chocolate-Chip Cookie", "unit":""},
                {"name":"Flour", "unit":"g"},
                {"name":"Penne", "unit":"g"},
                {"name":"Peanut", "unit":"g"},
                {"name":"Carrot", "unit":"g"},
            ]

            notfoods = [
                {"name":"Advil", "unit":"caps"},
                {"name":"Wood glue", "unit":"L"},
                {"name":"Toilet paper", "unit":""},
                {"name":"TidePods", "unit":""},
                {"name":"Handsoap", "unit":"L"},
            ]

            durables = [
                {"name":"Hammer", "unit":""},
            ]

            for item in foods:
                self.db_actions.add_food_type(**item)
            for item in notfoods:
                self.db_actions.add_notfood_type(**item)
            for item in durables:
                self.db_actions.add_durable_type(**item)

            for loc in ["Home", "Cabin"]:
                self.db_actions.add_location(name=loc)


            dry_storages = [
                {"storage_name":"Cupboard", "location_name":"Home", "capacity":0.1},
                {"storage_name":"Cellar", "location_name":"Cabin", "capacity":0.8},
                {"storage_name":"Pantry", "location_name":"Home", "capacity":0.5},
                {"storage_name":"Basement Shelves", "location_name":"Home", "capacity":0.7}
            ]
            fridge_storages = [
                {"storage_name":"Kitchen Fridge", "location_name":"Home", "capacity":0.65},
                {"storage_name":"Wine Fridge", "location_name":"Home", "capacity":0.3}
            ]
            freezer_storages = [
                {"storage_name":"Kitchen Freezer", "location_name":"Home", "capacity":0.65},
                {"storage_name":"Deep Freezer", "location_name":"Home", "capacity":0.84}
            ]

            for storage in dry_storages:
                self.db_actions.add_dry_storage(**storage)
            for storage in fridge_storages:
                self.db_actions.add_fridge_storage(**storage)
            for storage in freezer_storages:
                self.db_actions.add_freezer_storage(**storage)

            parents = [ "John", "Penny", "Jaquise" ]
            dependents = [ "Harry", "Han Solo", "Sarah" ]
            for parent in parents:
                self.db_actions.add_parent(name=parent)
            for dep in dependents:
                self.db_actions.add_dependent(name=dep)



        


    


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

                con = getattr(self.__parent, "_Database__connection", None)

                # Check if connection is None
                if con is None:
                    print("Connection is None")
                    return False

                # Check if connection is active
                if not con.is_connected():
                    print("Database is not connected")
                    return False

                cur = getattr(self.__parent, "_Database__cursor", None)

                # Check if cursor is indeed a cursor
                if cur is None:
                    print("Database cursor is None")
                    return False

                return True


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
                            # try:
                            result = old_func(*args, **kargs)
                            # except Exception as e:
                            #     # Failed to run old function
                            #     # TODO Handle error
                            #     print("SEVERE: AHHHHHH")
                            #     print(e.print)
                            #     print(old_func.__name__)
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
                        and not name.startswith("_")
                        and not name.endswith("__")
                        ):
                    replace_func(name) # Replace the function
            




        # ----- DYNAMIC -----

        def dynamic_query(self, group:str, function_name:str, **kargs) -> bool|list[RowType]:
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
            bool | list[RowType]
                If the statement is a `SELECT` query then the function returns a list 
                of tuples or dictionaries (`list[RowType]`). 
                Otherwise if the operation was successful returns `True`.
                If the operation fails for any reason (i.e. not all the required inputs
                that the function required were provided) then returns `False`.
            """

            # -- Get the query --
            query = None
            required_inputs = None
            expected_outputs = None
            try:
                query = self.__parent._Database__sql_statements.get_query(group = group, name = function_name)                       # Get query
                required_inputs = self.__parent._Database__sql_statements.get_query_inputs(group = group, name = function_name)      # Get query inputs
                expected_outputs = self.__parent._Database__sql_statements.get_query_outputs(group = group, name = function_name)    # Get query outputs
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

        def _add_item_type(self, name:str, unit:str) -> None:
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

            statement = self.__parent._Database__sql_statements.get_query(group = "ItemType", name = "Add item type")
            data = (name, unit)

            cursor.execute(statement, data)

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
            self._add_item_type(name, unit)


        def _select_item_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects item type records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            name : str
                The name of the item to search for.
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
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "ItemType", name = "Select item type")
            data = (name, unit)

            cursor.execute(statement, data)

            return cursor.fetchall()


        def select_item_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects item type records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            name : str
                The name of the item to search for.
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
            """
            return self._select_item_type(name, unit)
            

        def _add_item_type_subclass(self, subclass_name:str, name:str, unit:str="") -> None:
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
            try:
                self._add_item_type(name=name, unit=unit)
            except IntegrityError: pass # This is fine, It means it already exists

            # Create the subclass type
            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Add {subclass_name.lower()} type")
            data = (name,)

            cursor.execute(statement, data)


        def _select_item_type_subclass(self, subclass_name:str, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects records of an item type subclass from the database.

            Parameters
            ----------
            name : str
                The name of the item to search for.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            # Get the cursor
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name = f"Select {subclass_name.lower()} type")
            data = (name, unit)

            cursor.execute(statement, data)

            return cursor.fetchall()



        # ----- CONSUMABLE -----

        def _add_consumable_type(self, name:str, unit:str="") -> None:
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
            self._add_item_type_subclass(
                subclass_name="Consumable", 
                name=name,
                unit=unit
            )


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
            self._add_consumable_type(name, unit)


        def _select_consumable_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects consumable type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to search for.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type_subclass(
                subclass_name="Consumable",
                name=name,
                unit=unit
            )


        def _add_consumable_type_subclass(self, subclass_name:str, name:str, unit:str="") -> None:
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
            try:
                self._add_consumable_type(name=name, unit=unit)
            except IntegrityError: pass # This is fine, It means it already exists

            # Create the consumable subclass type
            self._add_item_type_subclass(
                subclass_name=subclass_name,
                name=name,
                unit=unit
            )



        # ----- DURABLE -----

        def _add_durable_type(self, name:str, unit:str="") -> None:
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
            self._add_item_type_subclass(
                subclass_name="Durable", 
                name=name,
                unit=unit
            )
        def add_durable_type(self, name:str, unit:str="") -> None:
            self._add_durable_type(name=name, unit=unit)


        def select_durable_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects durable type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to search for.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type_subclass(
                subclass_name="Durable",
                name=name,
                unit=unit
            )



        # ----- FOOD -----

        def _add_food_type(self, name:str, unit:str="") -> None:
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
            self._add_consumable_type_subclass(
                subclass_name="Food", 
                name=name,
                unit=unit
            )

        def add_food_type(self, name:str, unit:str="") -> None:
            self._add_food_type(name=name, unit=unit)


        def select_food_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects food type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to search for.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type_subclass(
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
            self._add_consumable_type_subclass(
                subclass_name="NotFood", 
                name=name,
                unit=unit
            )


        def select_notfood_type(self, name:str="%", unit:str="%") -> list[RowType]:
            """
            Selects not food type records from the database.

            Parameters
            ----------
            name : str
                The name of the item to search for.
                Example: "Milk"
            unit : str
                The unit that the item quantity is measured in.
                Example: "L"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type_subclass(
                subclass_name="NotFood",
                name=name,
                unit=unit
            )


        
        # ----- LOCATION -----

        def add_location(self, name:str) -> None:
            """
            Adds a location record to the database.

            Parameters
            ----------
            name : str
                The name of the location to add.
                Example: "Home"
                Example: "Smith Family Home"
                Example: "Winter Cabin"

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the location to add does not already exist in the table.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Add location")
            data = (name,)

            cursor.execute(statement, data)


        def delete_location(self, name:str) -> None:
            """
            Removes a location record to the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            name : str
                The name of the location to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the location to remove is not used elsewhere in the database.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Delete location")
            data = (name,)

            cursor.execute(statement, data)


        def select_locations(self, name:str="%") -> list[RowType]:
            """
            Selects location records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            name : str
                The name of the locaton to search for.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Select locations")
            data = (name,)

            cursor.execute(statement, data)

            return cursor.fetchall()


        
        # ----- STORAGE -----

        def _add_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            """
            Adds a storage record to the database.

            Parameters
            ----------
            storage_name : str
                The name of the storage to add.
            location_name : str
                The name of the location that the storage is in.
            capacity : float
                The percentage of the storage used.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to add does not already exist in the table.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Storage", name = "Add storage")
            data = (storage_name, location_name, capacity)

            cursor.execute(statement, data)


        def add_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            """
            Adds a storage record to the database.

            Parameters
            ----------
            storage_name : str
                The name of the storage to add.
            location_name : str
                The name of the location that the storage is in.
            capacity : float
                The percentage of the storage used.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to add does not already exist in the table.
            """
            self._add_storage(storage_name, location_name, capacity)


        def delete_storage(self, storage_name:str, return_warnings:bool=False) -> list|bool:
            """
            Removes a storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            storage_name : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """

            # Get the connection and cursor
            connection:MySQLConnection = self.__parent._Database__connection
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group="Storage", name = f"Delete storage")
            data = (storage_name,)  

            # Start the transaction
            connection.start_transaction(readonly=False)

            # Execute the delete
            cursor.execute(statement, data)

            # Get any warnings
            warnings = cursor.fetchwarnings()

            # Rollback if a warning occurs
            if type(warnings) is list and len(warnings) > 0:
                connection.rollback()
            else:
                connection.commit()
            
            # Return the list of warnings or the outcome of the operation
            if return_warnings:
                if type(warnings) is list:
                    return warnings
                else:
                    return []
            else:
                if type(warnings) is list:
                    return len(warnings) == 0
                else:
                    return True


        def select_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            """
            Selects storage records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            storage_name : str
                The name of the storage to search for.
            location_name : str
                The name of the location that the storage is in to search for.
            capacity_low : float
                The lower threshold value of the capacity.
            capacity_high : float
                The higher threshold value of the capacity.
                

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Storage", name = "Select storage")
            data = (storage_name, location_name, capacity_low, capacity_high)

            cursor.execute(statement, data)

            return cursor.fetchall()

    
        # ----- STORAGE SUBCLASSES -----


        def _add_storage_subclass(self, subclass_name:str, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            """
            Adds a storage subclass record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            subclass_name : str
                The name of the subclass.
            storage_name : str
                The name of the storage name to add.
            location_name : str
                The location of the new storage.
            capacity : float
                The initial capacity of the new storage.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            # Get the cursor
            cursor:MySQLCursor = self.__parent._Database__cursor

            # Create the item type if it doesn't exist
            try:
                self._add_storage(storage_name=storage_name, location_name=location_name, capacity=capacity)
            except IntegrityError: pass # This is fine, It means it already exists

            # Create the subclass type
            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Add {subclass_name.lower()} storage")
            data = (storage_name,)

            cursor.execute(statement, data)


        def add_dry_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            self._add_storage_subclass(
                subclass_name="Dry",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity
            )

    

        def _add_appliance_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            self._add_storage_subclass(
                subclass_name="Appliance",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity
            )

        def add_appliance_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            self._add_appliance_storage(
                    storage_name=storage_name,
                    location_name=location_name,
                    capacity=capacity
            )

        def _add_appliance_storage_subclass(self, subclass_name:str, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            try:
                self._add_appliance_storage(
                        storage_name=storage_name,
                        location_name=location_name,
                        capacity=capacity
                )
            except IntegrityError: pass # This is fine, It means it already exists

            self._add_storage_subclass(
                subclass_name=subclass_name,
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity
            )

        def add_fridge_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            self._add_appliance_storage_subclass(
                subclass_name="Fridge",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity
            )
            
        def add_freezer_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> None:
            self._add_appliance_storage_subclass(
                subclass_name="Freezer",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity
            )

        def _delete_storage_subclass(self, subclass_name:str, storage_name:str, return_warnings:bool=False) -> list|bool:

            # Get the connection and cursor
            connection:MySQLConnection = self.__parent._Database__connection
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name = f"Delete {subclass_name.lower()} storage")
            data = (storage_name,)  

            # Start the transaction
            connection.start_transaction(readonly=False)

            # Execute the delete
            cursor.execute(statement, data)

            # Get any warnings
            warnings = cursor.fetchwarnings()

            # Rollback if a warning occurs
            if type(warnings) is list and len(warnings) > 0:
                connection.rollback()
            else:
                connection.commit()
            
            # Return the list of warnings or the outcome of the operation
            if return_warnings:
                if type(warnings) is list:
                    return warnings
                else:
                    return []
            else:
                if type(warnings) is list:
                    return len(warnings) == 0
                else:
                    return True

        def delete_dry_storage(self, storage_name:str, return_warnings:bool=False) -> list|bool:
            return self._delete_storage_subclass(
                subclass_name="Dry",
                storage_name=storage_name,
                return_warnings=return_warnings
            )

        def delete_appliance_storage(self, storage_name:str, return_warnings:bool=False) -> list|bool:
            return self._delete_storage_subclass(
                subclass_name="Appliance",
                storage_name=storage_name,
                return_warnings=return_warnings
            )

        def delete_fridge_storage(self, storage_name:str, return_warnings:bool=False) -> list|bool:
            return self._delete_storage_subclass(
                subclass_name="Fridge",
                storage_name=storage_name,
                return_warnings=return_warnings
            )

        def delete_freezer_storage(self, storage_name:str, return_warnings:bool=False) -> list|bool:
            return self._delete_storage_subclass(
                subclass_name="Freezer",
                storage_name=storage_name,
                return_warnings=return_warnings
            )


        def _select_storage_subclass(self, subclass_name:str, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            """
            Selects records of a storage subclass from the database.

            Parameters
            ----------
            storage_name : str
                The name of the storage to search for.
            location_name : str
                The name of the location that the storage is in.
            capacity_low : float
                The lower bound of the current capacity of the storage.
            capacity_high : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            # Get the cursor
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Select {subclass_name.lower()} storage")
            data = (storage_name, location_name, capacity_low, capacity_high)  

            cursor.execute(statement, data)

            return cursor.fetchall()

        def select_dry_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            return self._select_storage_subclass(
                subclass_name="Dry",
                storage_name=storage_name,
                location_name=location_name,
                capacity_low=capacity_low,
                capacity_high=capacity_high
            )

        def select_appliance_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            return self._select_storage_subclass(
                subclass_name="Appliance",
                storage_name=storage_name,
                location_name=location_name,
                capacity_low=capacity_low,
                capacity_high=capacity_high
            )
        def select_fridge_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            return self._select_storage_subclass(
                subclass_name="Fridge",
                storage_name=storage_name,
                location_name=location_name,
                capacity_low=capacity_low,
                capacity_high=capacity_high
            )
        def select_freezer_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> list[RowType]:
            return self._select_storage_subclass(
                subclass_name="Freezer",
                storage_name=storage_name,
                location_name=location_name,
                capacity_low=capacity_low,
                capacity_high=capacity_high
            )
    

        # ----- User -----

        def _add_user(self, name:str) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Add user")
            data = (name,)

            cursor.execute(statement, data)

        def add_user(self, name:str) -> None:
            self._add_user(name=name)

        def add_parent(self, name:str) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor
            
            try:
                self._add_user(name=name)
            except IntegrityError: pass # This is fine, It means it already exists

            statement = self.__parent._Database__sql_statements.get_query(group = "Parent", name = "Add parent")
            data = (name,)

            cursor.execute(statement, data)

        def add_dependent(self, name:str) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor

            try:
                self._add_user(name=name)
            except IntegrityError: pass # This is fine, It means it already exists

            statement = self.__parent._Database__sql_statements.get_query(group = "Dependent", name = "Add dependent")
            data = (name,)

            cursor.execute(statement, data)

        def select_users(self, name:str="%") -> list[RowType]:
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Select users")
            data = (name,)

            cursor.execute(statement, data)

            return cursor.fetchall()

        def select_items_used_by_user(self, user_name:str="%") -> list[RowType]:
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Select items used by user")
            data = (user_name,)

            cursor.execute(statement, data)

            return cursor.fetchall()





        # ----- Inventory -----

        def _change_item_quantity(self, new_quantity:float, item_name:str, storage_name:str, timestamp:dt.datetime) -> bool:
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Change item quantity")
            data = (new_quantity,
                    item_name, 
                    storage_name,
                    timestamp
                    )

            try:
                cursor.execute(statement, data)
            except Exception:
                return False
            
            return True


        def change_item_quantity(self, new_quantity:float, item_name:str, storage_name:str, timestamp:dt.datetime) -> bool:
            return self._change_item_quantity(new_quantity=new_quantity, item_name=item_name, storage_name=storage_name, timestamp=timestamp)


        def _select_item_quantity_from_inventory(self, item_name:str, storage_name:str, timestamp:dt.datetime) -> float:
            cursor:MySQLCursor = self.__parent._Database__cursor

            existing_quantity = 0.0
            
            try:
                statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Select item quantity from inventory")
                data = (item_name, 
                        storage_name,
                        timestamp,
                        )
                cursor.execute(statement, data)
                existing_inventory = cursor.fetchone()
                if type(existing_inventory) is list and len(existing_inventory) > 0:
                    existing_quantity = existing_inventory[0]["quantity"]
            except:
                pass

            return existing_quantity




        def _add_item_to_inventory(
                self,
                item_name:str,
                storage_name:str,
                timestamp:dt.datetime=dt.datetime.now(),
                expiry:dt.datetime=dt.datetime.now() + dt.timedelta(days=10),
                quantity:float=1.0
            ) -> tuple[bool, str]:

            cursor:MySQLCursor = self.__parent._Database__cursor

            # Get existing inventory with these parameters
            quantity += self._select_item_quantity_from_inventory(
                item_name=item_name, 
                storage_name=storage_name,
                timestamp=timestamp
            )

            # Check item type exists
            if len(self._select_item_type(name=item_name)) == 0:
                return (False, "ItemType does not exist")

            
            # Try to add the item to inventory
            try:
                statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Add item to inventory")
                data = (item_name, storage_name, timestamp, expiry, quantity)
                cursor.execute(statement, data)
            except IntegrityError:
                self._change_item_quantity(
                    new_quantity=quantity,
                    item_name=item_name,
                    storage_name=storage_name,
                    timestamp=timestamp
                )
                return (True, "Updated quantity")


            return (True, "Added Item")

        def add_item_to_inventory(
                self,
                item_name:str,
                storage_name:str,
                timestamp:dt.datetime=dt.datetime.now(),
                expiry:dt.datetime=dt.datetime.now() + dt.timedelta(days=10),
                quantity:float=1.0
            ) -> tuple[bool, str]:
            return self._add_item_to_inventory(
                item_name=item_name,
                storage_name=storage_name,
                timestamp=timestamp,
                expiry=expiry,
                quantity=quantity
            )


        def view_inventory_items(
            self,
            item_name:str="%",
            storage_name:str="%",
            timestamp_from:dt.datetime=dt.datetime.min,
            timestamp_to:dt.datetime=dt.datetime.max
        ) -> list[RowType]:

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "View inventory items")
            data = (item_name, storage_name, timestamp_from, timestamp_to)
            cursor.execute(statement, data)

            return cursor.fetchall()

        def move_item_storage_location(
            self,
            new_storage_name:str,
            item_name:str,
            old_storage_name:str,
            timestamp:dt.datetime
        ) -> None:

            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Move item storage location")
            data = (new_storage_name, item_name, old_storage_name, timestamp)
            cursor.execute(statement, data)






















        # ----- History -----

        def _add_item_history_record(self, item_name:str, date_used:dt.datetime=dt.datetime.now(), quantity:float=1.0) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "History", name = "Add item history record")
            data = (item_name, date_used, quantity)

            cursor.execute(statement, data)


        def _add_item_wasted_record(self, item_name:str, date_used:dt.datetime=dt.datetime.now(), quantity:float=1.0) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor

            try:
                self._add_item_history_record(item_name=item_name, date_used=date_used, quantity=quantity)
            except Exception:
                print("Could not create item wasted record")
            else:
                statement = self.__parent._Database__sql_statements.get_query(group = "Wasted", name = "Add item wasted record")
                data = (item_name, date_used)

                cursor.execute(statement, data)


        def _add_item_used_record(self, item_name:str, date_used:dt.datetime=dt.datetime.now(), quantity:float=1.0) -> None:
            cursor:MySQLCursor = self.__parent._Database__cursor

            try:
                self._add_item_history_record(item_name=item_name, date_used=date_used, quantity=quantity)
            except Exception:
                print("Could not create item used record")
            else:
                statement = self.__parent._Database__sql_statements.get_query(group = "Used", name = "Add item used record")
                data = (item_name, date_used)

                cursor.execute(statement, data)






        # Miscellaneous actions (for now)

        def consume_inventory(self, item_name:str, storage_name:str, timestamp:dt.datetime, quantity:float, user:str) -> None:
            self._remove_and_log_inventory(item_name, storage_name, timestamp, quantity, user)

        def throw_out_inventory(self, item_name:str, storage_name:str, timestamp:dt.datetime, quantity:float) -> None:
            self._remove_and_log_inventory(item_name, storage_name, timestamp, quantity, None)

        def _remove_and_log_inventory(
            self,
            item_name:str,
            storage_name:str,
            timestamp:dt.datetime,
            quantity_removed:float,
            user:str|None
        ) -> None:

            cursor:MySQLCursor = self.__parent._Database__cursor

            try:
                self.__parent.start_transaction()

                self._select_item_quantity_from_inventory
                stmt1 = self.__parent._Database__sql_statements.get_query(group="Inventory", name="Select item quantity from inventory")
                data1 = (item_name, storage_name, timestamp)
                cursor.execute(stmt1, data1)

                old_quantity = cursor.fetchone()["quantity"] # TODO Handle null case (_remove_and_log_inventory MUST fail if it's null. -D)
                new_quantity = old_quantity - quantity_removed

                if new_quantity > 0:
                    stmt2 = self.__parent._Database__sql_statements.get_query(group="Inventory", name="Change item quantity")
                    data2 = (new_quantity, item_name, storage_name, timestamp)
                    cursor.execute(stmt2, data2)
                else:
                    stmt2 = self.__parent._Database__sql_statements.get_query(group="Inventory", name="Remove item from inventory")
                    data2 = (item_name, storage_name, timestamp)
                    cursor.execute(stmt2, data2)

                if user is None:
                    stmt3 = self.__parent._Database__sql_statements.get_query(group="Wasted", name="Add item wasted record")
                    data3 = (item_name, quantity_removed)
                    cursor.execute(stmt3, data3)
                else:
                    stmt3 = self.__parent._Database__sql_statements.get_query(group="Used", name="Add item used record")
                    data3 = (item_name, quantity_removed, user)
                    cursor.execute(stmt3, data3)
            except Error as e:
                print(e)
                # TODO Report failure of call.
                self.__parent.rollback()
            else:
                self.__parent.commit()
