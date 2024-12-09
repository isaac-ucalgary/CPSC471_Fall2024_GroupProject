# -- Library Imports --
from mysql.connector import Error, IntegrityError, InterfaceError, MySQLConnection
from mysql.connector.cursor import MySQLCursorDict
from types import FunctionType, MethodType
import datetime as dt
import inspect
import warnings


# -- Local Imports --
from env import MARIADB_HOST, MARIADB_PORT, MARIADB_DATABASE_NAME, MARIADB_USER
from secrets import MARIADB_PASSWORD # (ignore error, it's caused by .gitignore file and is expected.)
from sql_statements import SQL_Statements
from action_result import ActionResult


class Database:
    """
    A `Database` object is created to interact with a mysql style database.

    It connects to a database with provided parameters or those supplied in the `env.py` file 
    located in the same directory.
    A `secrets.py` file is also required to exist and be in the same directory as this class
    and it must contain a variable called `MARIADB_PASSWORD` which is the default password
    to use when connecting to the database.

    Requirements
    ------------
    `env.py`
        `MARIADB_HOST` : str
            The IP address or URL of the server of the database to connect to.

        `MARIADB_PORT` : int
            The port number of the database service running on the server.

        `MARIADB_DATABASE_NAME` : str
            The name of the database to use.

        `MARIADB_USER` : str
            The username used to connect to the database.

    `secrets.py`
        `MARIADB_PASSWORD` : str
            The password for the user that will be used to connect to the database.

    Attributes
    ----------
    `db_host` : str
        The IP address or URL of the database.

    `db_port` : int
        The port number that the database is connected on.

    `db_user` : str
        The username used to connect to the database.

    `db_name` : str
        The name of the database.

    `db_actions` : DB_Actions
        The instance of database actions at the disposal of this Database object 
        to use.
    """

    def __init__(self,
                 db_host:str=MARIADB_HOST,
                 db_port:int=MARIADB_PORT,
                 db_user:str=MARIADB_USER,
                 db_password:str=MARIADB_PASSWORD,
                 db_name:str=MARIADB_DATABASE_NAME,
                 auto_connect:bool=True
                 ):
        """
        Creates a database object to use to interact with a mysql database.

        Parameters
        ----------
        `db_host` : str
            The host address or url of the database to connect to.
            Defaults to the value in the env file.

        `db_port` : int
            The port of the database to connect to.
            Default in env.

        `db_user` : str
            The user name to connect to the database as.
            Default in env.

        `db_password` : str
            The password to use to connect to the database.
            Default in env.

        `db_name` : str
            The name of the database to use.
            Default in env.

        `auto_connect` : bool
            Whether to connect to the database as part of this initialization.
            Default True.
        """

        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        self.DB_CONN_CONFIG = {
            'host':self.db_host,
            'port':self.db_port,
            'user':self.db_user,
            'password':self.db_password,
            'collation':"utf8mb4_unicode_ci",
            'autocommit':True,
            'get_warnings':True,
            'time_zone':"MST"
        }

        # Initialize connection
        self.__connection:MySQLConnection = MySQLConnection()
        self.__cursor:MySQLCursorDict = MySQLCursorDict(self.__connection) # Ignore error

        if auto_connect:
            self.connect()

        self.db_actions = self.DB_Actions(self)

        self.__sql_statements = SQL_Statements()



    def connect(self, attempts:int=4, delay:int=0) -> bool:
        """
        Connects (or reconnects) to the database using the values provided in
        the initialization.
        Also creates a new `Cursor` object from the new connection to be
        able to interact with the database.


        Parameters
        ----------
        `attempts` : int
            The number of times to retry connecting to the database upon 
            connection failure.

        `delay` : int
            The time to wait inbetween retry attempts in seconds (integer only).


        Returns
        -------
        bool
            The status of if the connection was successful.
        """
        # Try to connect to the database.
        try:
            self.__connection.connect(**self.DB_CONN_CONFIG)
        except Error:
            try:
                # Terrible workaround for annoying connector code.
                self.__connection.reconnect(attempts=attempts-1, delay=delay)
            except InterfaceError:
                print("Failed to connect to the database")
                return False

        print("Connected to the database")

        # Make the cursor on the newly created connection.
        self.__cursor = MySQLCursorDict(self.__connection) # ignore error
        return True



    def close_connection(self) -> None:
        """
        Closes the cursor and disconnects from the database.
        """
        # Close cursor.
        if self.__cursor is not None:
            self.__cursor.close()

        # Close connection.
        if self.__connection is not None:
            self.__connection.disconnect()



    def close(self) -> None:
        """
        Alias for `close_connection()`.
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
        Only has effect if `start_transaction()` was already
        called. Calling `commit()` will also end said
        transaction.
        """
        if self.__connection is not None:
            self.__connection.commit()



    def rollback(self) -> None:
        """
        Rolls back any pending changes to the database.
        Only applies if `start_transaction()` was already 
        called. Calling `rollback()` will also end said
        transaction.
        """
        if self.__connection is not None:
            self.__connection.rollback()


    def build_database(self) -> bool:
        """
        Creates the database and all of the tables required for the app to operate.
        If the database or tables already exist it will not overwrite them but if 
        any are missing it will try to create them in the missing space even if
        the already existing tables do not satisfy the requirements for the new 
        table's existence. 
        If the current state of the database is degraded, it is recommended to
        delete the database prior to calling this function. Before doing so, back
        any data first. While this method is non-destructive, deleting the database
        is. There is no repair method so this is the only way to regenerate 
        the database to its intended state.
        """

        # Catch warnings as errors
        warnings.filterwarnings("error")

        # Nothing has failed yet
        operation_successful:bool = True
        connected_at_start = True

        # Get the ddl sql statements to build the database
        ddl = self.__sql_statements.get_ddl_sql_functions()

        # Connect to the database
        if not self.__connection.is_connected():
            operation_successful = self.connect() and operation_successful
            connected_at_start = False

        # Create the database and tables.
        if self.__connection.is_connected() and self.__cursor is not None:

            # Loop through the SQL statements for creating tables
            for function in ddl:
                function_name = function["function"]
                statement = function["query"]

                if type(statement) is str and type(function_name) is str:
                    # Execute the statement
                    try:
                        self.__cursor.execute(statement)
                    except Warning as w:
                        if "exists" not in str(w):
                            print(f"An error occurred whilst creating {function_name}. Not executing further statements.")
                            print(str(w))
                            operation_successful = False
                            break
                    else:
                        print(f"Success: {function_name}") # TODO Implement proper logging using the logging library

        else:
            operation_successful = False
            print(f"Connection failed, database {self.db_name} not created.")

        # Close the connection to the database
        if not connected_at_start:
            self.close_connection()

        # Reset the warning state
        warnings.resetwarnings()

        # Return the status of building the database
        return operation_successful


    def build_demo_database(self) -> None:
        """
        THIS IS A DESTRUCTIVE OPERATION!

        This method will drop the database along with all it's tables
        and data and then rebuild it as new.
        It will then populate the fresh database with default values.

        This is useful for demonstrating the application or for 
        testing purposes.
        """
        print("This will DROP the whole database and create the database from new and populate it with demo data.")
        print("\033[91mALL DATA WILL BE LOST\033[0m")
        accept_message = "RESET TO DEMO"
        user_input = input(f"To continue input \"{accept_message}\":")
        if user_input != accept_message:
            return None

        if self.connect() and self.__cursor is not None:

            # DROP DATABASE
            self.__cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name};")
            print(self.db_name)

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
                {"name":"Watermelon", "unit":""},
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


            inventory_items = [
                {"item_name":"Carrot", "storage_name":"Kitchen Fridge", "quantity":800, "expiry":dt.datetime.now() + dt.timedelta(days=30)},
                {"item_name":"Milk", "storage_name":"Kitchen Fridge", "quantity":3.5, "expiry":dt.datetime.now() + dt.timedelta(days=14, hours=19)},
                {"item_name":"Goldfish", "storage_name":"Pantry", "quantity":9000, "expiry":dt.datetime.now() + dt.timedelta(days=2000)},
                {"item_name":"Rice", "storage_name":"Basement Shelves", "quantity":2300, "expiry":None},
                {"item_name":"Pumpkin", "storage_name":"Kitchen Fridge", "quantity":150, "expiry":dt.datetime.now() + dt.timedelta(days=4)},
                {"item_name":"Hammer", "storage_name":"Basement Shelves", "quantity":1},
                {"item_name":"Toilet paper", "storage_name":"Basement Shelves", "quantity":33},
                {"item_name":"TidePods", "storage_name":"Basement Shelves", "quantity":90},
                {"item_name":"Ground Beef", "storage_name":"Deep Freezer", "quantity":500, "expiry":dt.datetime.now() + dt.timedelta(days=8)},
                {"item_name":"Chocolate-Chip Cookie", "storage_name":"Pantry", "quantity":13, "expiry":dt.datetime.now() + dt.timedelta(days=21)},
                {"item_name":"Potato", "storage_name":"Wine Fridge", "quantity":1},
                {"item_name":"Salmon", "storage_name":"Deep Freezer", "quantity":650, "expiry":dt.datetime.now() + dt.timedelta(days=11)},
                {"item_name":"Soup", "storage_name":"Deep Freezer", "quantity":1.6667, "expiry":dt.datetime.now() + dt.timedelta(days=45)},
                {"item_name":"Watermellon", "storage_name":"Kitchen Fridge", "quantity":1, "expiry":dt.datetime.now() + dt.timedelta(days=22)},
                {"item_name":"Spaghetti", "storage_name":"Cupboard", "quantity":800},
                {"item_name":"Haggis", "storage_name":"Kitchen Freezer", "quantity":4, "expiry":dt.datetime.now() + dt.timedelta(days=29)},
                {"item_name":"Potato", "storage_name":"Cellar", "quantity":46467},
                {"item_name":"Cheddar", "storage_name":"Kitchen Fridge", "quantity":500, "expiry":dt.datetime.now() + dt.timedelta(days=30)},
                {"item_name":"Advil", "storage_name":"Cupboard", "quantity":120},
                {"item_name":"Squash", "storage_name":"Kitchen Fridge", "quantity":1, "expiry":dt.datetime.now() + dt.timedelta(days=13)},
            ]

            for item in inventory_items:
                self.db_actions.add_item_to_inventory(**item)









    # ---------------------------- #
    # ----- DATABASE ACTIONS ----- #
    # ---------------------------- #

    class DB_Actions(object):
        """
        A Collection of methods used to interact with the database.
        This class requires that the json file consisting of all of 
        the sql statements exists and are correct.
        """

        def __init__(self, parent):
            """
            Creates a collection of database actions for the `parent` 
            `Database` object to use.

            All public functions will be pre_wrapped with error handling 
            as well as a connection check. 
            If the connection check fails, i.e. the connection to the 
            database was lost or was not initialized yet, then the
            action will not be run. It is the callers responsablity to 
            connect to the database prior to using a database action.
            """

            self.__parent = parent

            if not type(self.__parent) == Database:
                raise TypeError("Parent of all DB_Actions instances must be an instance of Database")


            def pre_func() -> bool:
                """
                The function to run before all public class methods.

                Checks that the parent database is connected prior
                to letting the function run.

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
                `name` : str
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
                            try:
                                result = old_func(*args, **kargs)
                            except Exception as e:
                                result = ActionResult(error_message="An unknown error occurred", exception=e)
                        else:
                            result = ActionResult(error_message="Function pre-conditions were not met. Function aborted.")
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

        def dynamic_query(self, group:str, function_name:str, **kargs) -> ActionResult:
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
            except KeyError as e:
                return ActionResult(error_message="Failed to get query information", exception=e)


            # -- Gather inputs from **kargs --
            inputs = []

            for key in required_inputs:
                if key not in kargs.keys():
                    return ActionResult(error_message="Missing key required for this query")
                else:
                    inputs.append(kargs[key])

            inputs = tuple(inputs)


            # -- Execute the SQL statement --
            cursor:MySQLCursorDict = self.__parent._Database__cursor
            cursor.execute(query, inputs)


            # -- Get outputs --
            if len(expected_outputs) > 0:
                return ActionResult(data=cursor.fetchall())
            else:
                return ActionResult(success=True)




        # ----- ITEM TYPE -----

        def _add_item_type(self, name:str, unit:str) -> ActionResult:
            """
            Adds an item type record to the database.

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "ItemType", name = "Add item type")
            data = (name, unit)

            try: 
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to add item type", exception=e)
            else:
                return ActionResult()



        def add_item_type(self, name:str, unit:str) -> ActionResult:
            """
            Adds an item type record to the database.

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self._add_item_type(name, unit)



        def _select_item_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects item type records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"
                Example: "M%"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"
                Example: "%"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "ItemType", name = "Select item type")
            data = (name, unit)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        def select_item_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects item type records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"
                Example: "M%"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"
                Example: "%"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type(name, unit)



        def _add_item_type_subclass(self, subclass_name:str, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds an item type subclass record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            `subclass_name` : str
                The name of the subclass table to create the item in.

            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """

            # Get the cursor
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Create the item type if it doesn't exist
            if create_parents:
                add_item_type_exception = self._add_item_type(name=name, unit=unit).get_exception()
                if add_item_type_exception not in [IntegrityError, None]:
                    return ActionResult(error_message=f"Failed to add item type", exception=add_item_type_exception)

            # Create the subclass type
            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Add {subclass_name.lower()} type")
            data = (name,)

            # Execute the query and return the result
            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message=f"Failed to add {subclass_name} type", exception=e)
            else:
                return ActionResult()



        def _select_item_type_subclass(self, subclass_name:str, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects records of an item type subclass from the database.

            Parameters
            ----------
            `subclass_name` : str
                The name of the subclass table to select the item from.

            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            # Get the cursor
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name = f"Select {subclass_name.lower()} type")
            data = (name, unit)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        # ----- CONSUMABLE -----

        def _add_consumable_type(self, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds a consumable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self._add_item_type_subclass(
                subclass_name="Consumable", 
                name=name,
                unit=unit,
                create_parents=create_parents
            )



        def add_consumable_type(self, name:str, unit:str="") -> ActionResult:
            """
            Adds a consumable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self._add_consumable_type(name, unit, True)



        def _select_consumable_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects consumable type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
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



        def _add_consumable_type_subclass(self, subclass_name:str, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds a consumable type subclass record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            `subclass_name` : str
                The name of the subclass to create an item for.

            `name` : str
                The name of the item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            # Create the consumable type if it doesn't exist
            if create_parents:
                add_consumable_exception = self._add_consumable_type(name=name, unit=unit, create_parents=True).get_exception()
                if add_consumable_exception not in [IntegrityError, None]:
                    return ActionResult(error_message=f"Failed to add consumable type", exception=add_consumable_exception)

            # Create the consumable subclass type
            return self._add_item_type_subclass(
                subclass_name=subclass_name,
                name=name,
                unit=unit,
                create_parents=False
            )



        # ----- DURABLE -----

        def _add_durable_type(self, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds a durable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Hammer"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "" (What are you measuring hammers in?)

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self._add_item_type_subclass(
                subclass_name="Durable", 
                name=name,
                unit=unit,
                create_parents=create_parents
            )



        def add_durable_type(self, name:str, unit:str="") -> ActionResult:
            """
            Adds a durable type record to the database.
            Also creates the respective item type record as well if
            it doesn't already exist using the optional `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the item to add.
                Example: "Hammer"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "" (What are you measuring hammers in?)


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the item to add does not already exist in the table.
            """
            return self._add_durable_type(name=name, unit=unit, create_parents=True)



        def _select_durable_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects durable type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
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



        def select_durable_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects durable type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_durable_type(name=name, unit=unit)



        # ----- FOOD -----

        def _add_food_type(self, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds a food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the food item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the food item to add does not already exist in the table.
            """
            return self._add_consumable_type_subclass(
                subclass_name="Food", 
                name=name,
                unit=unit,
                create_parents=create_parents
            )



        def add_food_type(self, name:str, unit:str="") -> ActionResult:
            """
            Adds a food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the food item to add.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the food item to add does not already exist in the table.
            """
            return self._add_food_type(name=name, unit=unit, create_parents=True)



        def _select_food_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects food type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
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



        def select_food_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects food type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_food_type(name=name, unit=unit)



        # ----- NOT FOOD -----

        def _add_notfood_type(self, name:str, unit:str="", create_parents:bool=True) -> ActionResult:
            """
            Adds a not food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the not item to add.
                Example: "TidePods"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "kg"

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the not food item to add does not already exist in the table.
            """
            return self._add_consumable_type_subclass(
                subclass_name="NotFood", 
                name=name,
                unit=unit,
                create_parents=create_parents
            )



        def add_notfood_type(self, name:str, unit:str="") -> ActionResult:
            """
            Adds a not food type record to the database.
            Also creates respective consumable and item type records 
            as well if they don't already exist using the optional 
            `unit` option. 

            Parameters
            ----------
            `name` : str
                The name of the not item to add.
                Example: "TidePods"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "kg"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the not food item to add does not already exist in the table.
            """
            return self._add_notfood_type(name=name, unit=unit, create_parents=True)



        def _select_notfood_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects not food type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_item_type_subclass( subclass_name="NotFood",
                                                   name=name,
                                                   unit=unit
                                                   )



        def select_notfood_type(self, name:str="%", unit:str="%") -> ActionResult:
            """
            Selects not food type records from the database.

            Parameters
            ----------
            `name` : str
                The name of the item to search for.
                Example: "Milk"

            `unit` : str
                The unit that the item quantity is measured in.
                Example: "L"


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_notfood_type(name=name, unit=unit)



        # ----- LOCATION -----

        def add_location(self, name:str) -> ActionResult:
            """
            Adds a location record to the database.

            Parameters
            ----------
            `name` : str
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
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Add location")
            data = (name,)

            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to create location", exception=e)
            else:
                return ActionResult()



        def delete_location(self, name:str) -> ActionResult:
            """
            Removes a location record to the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `name` : str
                The name of the location to delete.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `name` of the location to remove is not used elsewhere in the database.
            """

            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Delete location")
            data = (name,)

            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to delete location", exception=e)
            else:
                return ActionResult()



        def select_locations(self, name:str="%") -> ActionResult:
            """
            Selects location records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            `name` : str
                The name of the locaton to search for.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Location", name = "Select locations")
            data = (name,)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        # ----- STORAGE -----

        def _add_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> ActionResult:
            """
            Adds a storage record to the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to add.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity` : float
                The percentage of the storage used.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to add does not already exist in the table.
            """

            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Storage", name = "Add storage")
            data = (storage_name, location_name, capacity)

            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to create storage", exception=e)
            else:
                return ActionResult()



        def add_storage(self, storage_name:str, location_name:str, capacity:float=0.0) -> ActionResult:
            """
            Adds a storage record to the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to add.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity` : float
                The percentage of the storage used.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to add does not already exist in the table.
            """
            return self._add_storage(storage_name, location_name, capacity)



        def delete_storage(self, storage_name:str) -> ActionResult:
            """
            Removes a storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """

            # Get the connection and cursor
            connection:MySQLConnection = self.__parent._Database__connection
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group="Storage", name = f"Delete storage")
            data = (storage_name,)  

            # Start the transaction
            connection.start_transaction(readonly=False)

            # Execute the delete
            cursor.execute(statement, data)

            # Get any warnings
            warnings = cursor.fetchwarnings()

            # Rollback if a warning occurs and return the outcome
            if type(warnings) is list and len(warnings) > 0:
                connection.rollback()
                return ActionResult(success=False, warnings=warnings)
            else:
                connection.commit()
                return ActionResult(success=True)



        def select_storage(self, storage_name:str="%", location_name:str="%", capacity_low:float=0.0, capacity_high:float=2.0) -> ActionResult:
            """
            Selects storage records from the database.
            Used SQL style regex for searching.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in to search for.

            `capacity_low` : float
                The lower threshold value of the capacity.

            `capacity_high` : float
                The higher threshold value of the capacity.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Storage", name = "Select storage")
            data = (storage_name, location_name, capacity_low, capacity_high)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        # ----- STORAGE SUBCLASSES -----

        def _add_storage_subclass(self,
                                  subclass_name:str,
                                  storage_name:str,
                                  location_name:str,
                                  capacity:float=0.0,
                                  create_parents:bool=True
                                  ) -> ActionResult:
            """
            Adds a storage subclass record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `subclass_name` : str
                The name of the subclass.

            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            # Get the cursor
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Create the item type if it doesn't exist
            if create_parents:
                add_storage_exception = self._add_storage(storage_name=storage_name, location_name=location_name, capacity=capacity).get_exception()
                if add_storage_exception not in [IntegrityError, None]:
                    return ActionResult(error_message="Failed to create storage", exception=add_storage_exception)


            # Create the subclass type
            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Add {subclass_name.lower()} storage")
            data = (storage_name,)

            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message=f"Failed to create {subclass_name} storage", exception=e)
            else:
                return ActionResult()



        def _add_dry_storage(self,
                             storage_name:str,
                             location_name:str,
                             capacity:float=0.0,
                             create_parents:bool=True
                             ) -> ActionResult:
            """
            Adds a dry storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_storage_subclass( 
                subclass_name="Dry",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity,
                create_parents=create_parents
            )



        def add_dry_storage(self,
                            storage_name:str,
                            location_name:str,
                            capacity:float=0.0
                            ) -> ActionResult:
            """
            Adds a dry storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_dry_storage( 
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity,
                create_parents=True
            )



        def _add_appliance_storage(self,
                                   storage_name:str,
                                   location_name:str,
                                   capacity:float=0.0,
                                   create_parents:bool=True
                                   ) -> ActionResult:
            """
            Adds a appliance storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_storage_subclass(
                subclass_name="Appliance",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity,
                create_parents=create_parents
            )



        def add_appliance_storage(self,
                                  storage_name:str,
                                  location_name:str,
                                  capacity:float=0.0
                                  ) -> ActionResult:
            """
            Adds a appliance storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_appliance_storage(
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity,
                create_parents=True
            )



        def _add_appliance_storage_subclass(self,
                                            subclass_name:str,
                                            storage_name:str,
                                            location_name:str,
                                            capacity:float=0.0,
                                            create_parents:bool=True
                                            ) -> ActionResult:
            """
            Adds an appliance storage subclass record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `subclass_name` : str
                The name of the subclass.

            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent storage records prior to adding this item.


            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            # Add the appliance if it doesn't already exist
            if create_parents:
                add_appliance_exception = self._add_appliance_storage(
                    storage_name=storage_name,
                    location_name=location_name,
                    capacity=capacity,
                    create_parents=True
                ).get_exception()
                if add_appliance_exception not in [IntegrityError, None]:
                    return ActionResult(error_message="Failed to appliance storage", exception=add_appliance_exception)

            # Add the subclass
            return self._add_storage_subclass(subclass_name=subclass_name,
                                              storage_name=storage_name,
                                              location_name=location_name,
                                              capacity=capacity,
                                              create_parents=False)



        def _add_fridge_storage(self,
                                storage_name:str,
                                location_name:str,
                                capacity:float=0.0,
                                create_parents:bool=True
                                ) -> ActionResult:
            """
            Adds a fridge storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_appliance_storage_subclass(subclass_name="Fridge",
                                                        storage_name=storage_name,
                                                        location_name=location_name,
                                                        capacity=capacity,
                                                        create_parents=create_parents)



        def add_fridge_storage(self,
                               storage_name:str,
                               location_name:str,
                               capacity:float=0.0
                               ) -> ActionResult:
            """
            Adds a fridge storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_fridge_storage(storage_name=storage_name,
                                            location_name=location_name,
                                            capacity=capacity,
                                            create_parents=True)



        def _add_freezer_storage(self,
                                 storage_name:str,
                                 location_name:str,
                                 capacity:float=0.0,
                                 create_parents:bool=True
                                 ) -> ActionResult:
            """
            Adds a freezer storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            `create_parents` : bool
                Whether to create the parent records prior to adding this item.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_appliance_storage_subclass(
                subclass_name="Freezer",
                storage_name=storage_name,
                location_name=location_name,
                capacity=capacity,
                create_parents=create_parents
            )



        def add_freezer_storage(self,
                                storage_name:str,
                                location_name:str,
                                capacity:float=0.0
                                ) -> ActionResult:
            """
            Adds a freezer storage record to the database.
            Also creates the respective storage record as well if
            it doesn't already exist using the `location_name` parameter. 

            Parameters
            ----------
            `storage_name` : str
                The name of the storage name to add.

            `location_name` : str
                The location of the new storage.

            `capacity` : float
                The initial capacity of the new storage.
                Between 0 and 2.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._add_freezer_storage(storage_name=storage_name,
                                             location_name=location_name,
                                             capacity=capacity,
                                             create_parents=True)



        def _delete_storage_subclass(self,
                                     subclass_name:str,
                                     storage_name:str
                                     ) -> ActionResult:
            """
            Removes a storage record from the database of the desired subclass.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `subclass_name` : str
                The name of the storage subclass.

            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """
            # Get the connection and cursor
            connection:MySQLConnection = self.__parent._Database__connection
            cursor:MySQLCursorDict = self.__parent._Database__cursor

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
                return ActionResult(success=False, warnings=warnings)
            else:
                connection.commit()
                return ActionResult(success=True)



        def delete_dry_storage(self, storage_name:str) -> ActionResult:
            """
            Removes a dry storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """
            return self._delete_storage_subclass( subclass_name="Dry", storage_name=storage_name )



        def delete_appliance_storage(self, storage_name:str) -> ActionResult:
            """
            Removes an appliance storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """
            return self._delete_storage_subclass( subclass_name="Appliance", storage_name=storage_name )



        def delete_fridge_storage(self, storage_name:str) -> ActionResult:
            """
            Removes a fridge storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """
            return self._delete_storage_subclass( subclass_name="Fridge", storage_name=storage_name )



        def delete_freezer_storage(self, storage_name:str) -> ActionResult:
            """
            Removes a freezer storage record from the database.
            The location must not be used by anywhere else in the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to delete.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            - The `storage_name` of the storage to remove is not used elsewhere in the database.
            """
            return self._delete_storage_subclass( subclass_name="Freezer", storage_name=storage_name )



        def _select_storage_subclass(self,
                                     subclass_name:str,
                                     storage_name:str="%",
                                     location_name:str="%",
                                     capacity_low:float=0.0,
                                     capacity_high:float=2.0
                                     ) -> ActionResult:
            """
            Selects records of a storage subclass from the database.

            Parameters
            ----------
            `subclass_name` : str
                The name of the storage subclass to select from.

            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity_low` : float
                The lower bound of the current capacity of the storage.

            `capacity_high` : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """

            # Get the cursor
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group=subclass_name, name=f"Select {subclass_name.lower()} storage")
            data = (storage_name, location_name, capacity_low, capacity_high)  

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        def select_dry_storage(self,
                               storage_name:str="%",
                               location_name:str="%",
                               capacity_low:float=0.0,
                               capacity_high:float=2.0
                               ) -> ActionResult:
            """
            Selects dry storage records from the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity_low` : float
                The lower bound of the current capacity of the storage.

            `capacity_high` : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_storage_subclass(subclass_name="Dry",
                                                 storage_name=storage_name,
                                                 location_name=location_name,
                                                 capacity_low=capacity_low,
                                                 capacity_high=capacity_high)



        def select_appliance_storage(self,
                                     storage_name:str="%",
                                     location_name:str="%",
                                     capacity_low:float=0.0,
                                     capacity_high:float=2.0
                                     ) -> ActionResult:
            """
            Selects appliance storage records from the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity_low` : float
                The lower bound of the current capacity of the storage.

            `capacity_high` : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_storage_subclass(subclass_name="Appliance",
                                                 storage_name=storage_name,
                                                 location_name=location_name,
                                                 capacity_low=capacity_low,
                                                 capacity_high=capacity_high)



        def select_fridge_storage(self,
                                  storage_name:str="%",
                                  location_name:str="%",
                                  capacity_low:float=0.0,
                                  capacity_high:float=2.0
                                  ) -> ActionResult:
            """
            Selects fridge storage records from the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity_low` : float
                The lower bound of the current capacity of the storage.

            `capacity_high` : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_storage_subclass(subclass_name="Fridge",
                                                 storage_name=storage_name,
                                                 location_name=location_name,
                                                 capacity_low=capacity_low,
                                                 capacity_high=capacity_high)



        def select_freezer_storage(self,
                                   storage_name:str="%",
                                   location_name:str="%",
                                   capacity_low:float=0.0,
                                   capacity_high:float=2.0
                                   ) -> ActionResult:
            """
            Selects freezer storage records from the database.

            Parameters
            ----------
            `storage_name` : str
                The name of the storage to search for.

            `location_name` : str
                The name of the location that the storage is in.

            `capacity_low` : float
                The lower bound of the current capacity of the storage.

            `capacity_high` : float
                The higher bound of the current capacity of the storage.

            Assumptions
            -----------
            - The database connection is open.
            - The database connection cursor is open.
            """
            return self._select_storage_subclass(subclass_name="Freezer",
                                                 storage_name=storage_name,
                                                 location_name=location_name,
                                                 capacity_low=capacity_low,
                                                 capacity_high=capacity_high)



        # ----- User -----

        def _add_user(self, name:str) -> ActionResult:
            """
            Adds a user to the database.

            Parameters
            ----------
            `name` : str
                The name of the user to add.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Add user")
            data = (name,)

            try:
                cursor.execute(statement, data)
            except IntegrityError as e:
                return ActionResult(error_message="User already exists", exception=e)
            except Exception as e:
                return ActionResult(error_message="Failed to add user", exception=e)
            else:
                return ActionResult()



        def add_user(self, name:str) -> ActionResult:
            """
            Adds a user to the database.

            Parameters
            ----------
            `name` : str
                The name of the user to add.
            """
            return self._add_user(name=name)



        def add_parent(self, name:str) -> ActionResult:
            """
            Adds a parent user to the database.

            Parameters
            ----------
            `name` : str
                The name of the user to add.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Add user if it doesn't already exist
            add_user_result = self._add_user(name=name)
            if add_user_result.get_exception() not in [IntegrityError, None]:
                return add_user_result

            statement = self.__parent._Database__sql_statements.get_query(group = "Parent", name = "Add parent")
            data = (name,)

            # Add the parent
            try:
                cursor.execute(statement, data)
            except IntegrityError as e:
                return ActionResult(error_message="Parent already exists", exception=e)
            except Exception as e:
                return ActionResult(error_message="Failed to add parent", exception=e)
            else:
                return ActionResult()



        def add_dependent(self, name:str) -> ActionResult:
            """
            Adds a dependent user to the database.

            Parameters
            ----------
            `name` : str
                The name of the user to add.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Add the user if it doesn't already exist
            add_user_result = self._add_user(name=name)
            if add_user_result.get_exception() not in [IntegrityError, None]:
                return add_user_result

            statement = self.__parent._Database__sql_statements.get_query(group = "Dependent", name = "Add dependent")
            data = (name,)

            # Add the dependent
            try:
                cursor.execute(statement, data)
            except IntegrityError as e:
                return ActionResult(error_message="Dependent already exists", exception=e)
            except Exception as e:
                return ActionResult(error_message="Failed to add dependent", exception=e)
            else:
                return ActionResult()



        def _select_users(self, name:str="%") -> ActionResult:
            """
            Gets a list of all the users.

            Parameters
            ----------
            `name` : str
                The name of the user to select.
                Supports MySQL regex.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Select users")
            data = (name,)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        def select_users(self, name:str="%") -> ActionResult:
            """
            Gets a list of all the users.

            Parameters
            ----------
            `name` : str
                The name of the user to select.
                Supports MySQL regex.
            """
            return self._select_users(name=name)



        def _select_parents(self, name:str="%") -> ActionResult:
            """
            Gets a list of all the parents.

            Parameters
            ----------
            `name` : str
                The name of the user to select.
                Supports MySQL regex.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Parent", name = "Select parents")
            data = (name,)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        def select_parents(self, name:str="%") -> ActionResult:
            """
            Gets a list of all the parents.

            Parameters
            ----------
            `name` : str
                The name of the user to select.
                Supports MySQL regex.
            """
            return self._select_parents(name=name)



        def select_items_used_by_user(self, user_name:str="%") -> ActionResult:
            """
            Selects all the items used by a user.

            Parameters
            ----------
            `user_name` : str
                Gets all the items used by this user.
                Supports MySQL regex.

            Examples
            --------
            `select_items_used_by_user("Jimmy")` 
                Would get all the items used by `Jimmy`.

            `select_items_used_by_user("%Smith")` 
                Would get all the items used by either someone called `Smith` or
                by all `users` with the surname `Smith`.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "User", name = "Select items used by user")
            data = (user_name,)

            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        # ----- Inventory -----

        def _change_item_quantity(self,
                                  new_quantity:float,
                                  item_name:str,
                                  storage_name:str,
                                  timestamp:dt.datetime
                                  ) -> ActionResult:
            """
            Changes the quantity of an `item` in inventory.

            Parameters
            ----------
            `new_quantity` : float
                The new quantity of the `item`.

            `item_name` : str
                The name of the `item` to change the quantity of.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of the `item` when it was added.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Change item quantity")
            data = (new_quantity, item_name, storage_name, timestamp)

            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to update item quantity", exception=e)
            else:
                return ActionResult()



        def change_item_quantity(self,
                                 new_quantity:float,
                                 item_name:str,
                                 storage_name:str,
                                 timestamp:dt.datetime
                                 ) -> ActionResult:
            """
            Changes the quantity of an `item` in inventory.

            Parameters
            ----------
            `new_quantity` : float
                The new quantity of the `item`.

            `item_name` : str
                The name of the `item` to change the quantity of.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of the `item` when it was added.
            """
            return self._change_item_quantity(new_quantity=new_quantity,
                                              item_name=item_name,
                                              storage_name=storage_name,
                                              timestamp=timestamp)



        def _select_item_quantity_from_inventory(self,
                                                 item_name:str,
                                                 storage_name:str,
                                                 timestamp:dt.datetime
                                                 ) -> float:
            """
            Gets the quantiy of an item in inventory.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of the `item` when it was added.

            Returns
            -------
            float
                The quantity of the `item`.
                If the item does not exist; returns 0.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            existing_quantity = 0.0

            try:
                statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Select item quantity from inventory")
                data = (item_name, storage_name, timestamp)
                cursor.execute(statement, data)
                existing_inventory = cursor.fetchone()
                if type(existing_inventory) is list and len(existing_inventory) > 0:
                    existing_quantity = existing_inventory[0]["quantity"]
            except:
                pass

            return existing_quantity




        def _add_item_to_inventory(self,
                                   item_name:str,
                                   storage_name:str,
                                   expiry:dt.datetime|None=None,
                                   quantity:float=1.0
                                   ) -> ActionResult:
            """
            Adds an item to inventory.
            Uses the current timestamp to create the item.

            Will not increase the quantity of an item if it already exists.
            Since this uses the current timestamp, the possibility of 
            trying to create an item and it already existing is very small.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `expiry` : datetime
                The datetime of when the item will expire.
                None if the item does not expire, or is a non-perishable.

            `quantity` : float
                The quantity of the item to add.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Check item type exists
            select_item_data = self._select_item_type(name=item_name).get_data()
            if type(select_item_data) is not list or len(select_item_data) == 0:
                return ActionResult(error_message="ItemType does not exist")

            # Try to add the item to inventory
            try:
                statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Add item to inventory")
                data = (item_name, storage_name, expiry, quantity)
                cursor.execute(statement, data)
            except IntegrityError as e:
                if "FOREIGN" in str(e) and "storage_name" in str(e):
                    return ActionResult(error_message="Storage location does not exist", exception=e)
                else:
                    return ActionResult(error_message="Item already exists in inventory", exception=e)
            except Exception as e:
                return ActionResult(error_message="Failed to add item to inventory", exception=e)

            return ActionResult(success=True)



        def add_item_to_inventory(self, 
                                  item_name:str, 
                                  storage_name:str, 
                                  expiry:dt.datetime|None=None, 
                                  quantity:float=1.0
                                  ) -> ActionResult:
            """
            Adds an item to inventory.
            Uses the current timestamp to create the item.

            Will not increase the quantity of an item if it already exists.
            Since this uses the current timestamp, the possibility of 
            trying to create an item and it already existing is very small.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `expiry` : datetime
                The datetime of when the item will expire.
                None if the item does not expire, or is a non-perishable.

            `quantity` : float
                The quantity of the item to add.
            """
            return self._add_item_to_inventory(item_name=item_name, 
                                               storage_name=storage_name, 
                                               expiry=expiry, 
                                               quantity=quantity)



        def view_inventory_items(self,
                                 item_name:str="",
                                 storage_name:str="",
                                 expiry_from:dt.datetime|None=None,
                                 expiry_to:dt.datetime|None=None,
                                 include_non_perishable:bool=True
                                 ) -> ActionResult:
            """
            Selects all the items that match the search parameters.

            Parameters
            ----------
            `item_name` : str
                The name of the `item` to search for.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `expiry_from` : datetime | None
                The lower bound datetime of when the item will expire.
                Use `None` to not include a lower bound.

            `expiry_to` : datetime | None
                The upper bound datetime of when the item will expire.
                Use `None` to not include a upper bound.

            `include_non_perishable` : bool
                Whether to include items that don't have an expiry date.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # TODO This should be its own function and be applied to all LIKE clauses.
            # Escape characters
            item_name.replace("%", "!%")
            item_name.replace("!", "!!")
            storage_name.replace("%", "!%")
            storage_name.replace("!", "!!")

            item_name = f"%{item_name}%"
            storage_name = f"%{storage_name}%"

            # Set min and max values for the expiry range
            if expiry_from is None: expiry_from = dt.datetime.min
            if expiry_to is None: expiry_to = dt.datetime.max

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "View inventory items")
            data = (item_name, storage_name, expiry_from, expiry_to, include_non_perishable)
            cursor.execute(statement, data)

            return ActionResult(data=cursor.fetchall())



        def move_item_storage_location(self,
                                       new_storage_name:str,
                                       item_name:str,
                                       old_storage_name:str,
                                       timestamp:dt.datetime
                                       ) -> ActionResult:
            """
            Moves an item from one storage location to another.

            Parameters
            ----------
            `new_storage_name` : str
                The name of the storage to move the item to.

            `item_name` : str
                The name of the `item` to move.

            `old_storage_name` : str
                The current name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of the `item` when it was added.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Move item storage location")
            data = (new_storage_name, item_name, old_storage_name, timestamp)

            # Try to move the item
            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to move item", exception=e)

            return ActionResult(success=True)



        def _remove_item_from_inventory(self,
                                        item_name:str,
                                        storage_name:str,
                                        timestamp:dt.datetime
                                        ) -> ActionResult:
            """
            Adds an item to inventory.
            Uses the current timestamp to create the item.

            Will not increase the quantity of an item if it already exists.
            Since this uses the current timestamp, the possibility of 
            trying to create an item and it already existing is very small.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of when the `item` was added.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            statement = self.__parent._Database__sql_statements.get_query(group = "Inventory", name = "Remove item from inventory")
            data = (item_name, storage_name, timestamp)

            # Try to delete the item
            try:
                cursor.execute(statement, data)
            except Exception as e:
                return ActionResult(error_message="Failed to delete item", exception=e)

            return ActionResult(success=True)



        def consume_inventory(self,
                              item_name:str,
                              storage_name:str,
                              timestamp:dt.datetime,
                              quantity:float,
                              user:str
                              ) -> ActionResult:
            """
            Removes an item from the inventory and logs it
            as consumed.

            If the desired quantity to remove is move than what 
            is currently left in inventory then the quantity
            remaining will be what is logged and the inventory 
            record will be removed.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of when the `item` was added.

            `quantity` : float
                The desired quantity of the item to consume.

            `user` : str
                The name of the user who used the item.
            """
            return self._remove_and_log_inventory(item_name=item_name,
                                                  storage_name=storage_name,
                                                  timestamp=timestamp,
                                                  quantity_removed=quantity,
                                                  user=user)



        def throw_out_inventory(self,
                                item_name:str,
                                storage_name:str,
                                timestamp:dt.datetime,
                                quantity:float
                                ) -> ActionResult:
            """
            Removes an item from the inventory and logs it
            as wasted.

            If the desired quantity to remove is move than what 
            is currently left in inventory then the quantity
            remaining will be what is logged and the inventory 
            record will be removed.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of when the `item` was added.

            `quantity` : float
                The desired quantity of the item to throw out.
            """
            return self._remove_and_log_inventory(item_name, storage_name, timestamp, quantity, None)



        def _remove_and_log_inventory(self,
                                      item_name:str,
                                      storage_name:str,
                                      timestamp:dt.datetime,
                                      quantity_removed:float,
                                      user:str|None
                                      ) -> ActionResult:
            """
            Removes an item from the inventory and logs it.

            If the desired quantity to remove is move than what 
            is currently left in inventory then the quantity
            remaining will be what is logged and the inventory 
            record will be removed.

            Parameters
            ----------
            `item_name` : str
                The name of the `item`.

            `storage_name` : str
                The name of the storage location the `item` is stored in.

            `timestamp` : datetime
                The timestamp of when the `item` was added.

            `quantity_removed` : float
                The desired quantity of the item to remove.

            `user` : str | None
                The name of the user who used the item.
                If this value is `None` then the item will be logged 
                as wasted.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Start a database transaction
            self.__parent.start_transaction()

            # Calculate the new quantity of the item
            new_quantity:float
            try:
                stmt1 = self.__parent._Database__sql_statements.get_query(group="Inventory", name="Select item quantity from inventory")
                data1 = (item_name, storage_name, timestamp)
                cursor.execute(stmt1, data1)
                value = cursor.fetchone()
                if type(value) is dict:
                    # This handles weird RowItemType conversions because MySQL has no good documentation
                    old_quantity = str(value["quantity"]) 
                    new_quantity = float(old_quantity) - quantity_removed
                else:
                    raise ValueError("The quantity of the item could not be collected because the item does not exist in inventory");
            except Exception as e:
                self.__parent.rollback()
                return ActionResult(error_message="Failed to get inventory quantity", exception=e)


            # Reduce the quantity of the item by the desired amount or remove the item if its quantity has been exhausted.
            result:ActionResult
            if new_quantity > 0:
                result = self._change_item_quantity(new_quantity, item_name, storage_name, timestamp)
            else:
                result = self._remove_item_from_inventory(item_name, storage_name, timestamp)

            # Rollback and return if the change quantity operation was not successful
            if not result.is_success():
                self.__parent.rollback()
                return result

            # Log the usage of the item
            try:
                if user is None:
                    stmt = self.__parent._Database__sql_statements.get_query(group="Wasted", name="Add item wasted record")
                    data = (item_name, quantity_removed)
                    cursor.execute(stmt, data)
                else:
                    stmt = self.__parent._Database__sql_statements.get_query(group="Used", name="Add item used record")
                    data = (item_name, quantity_removed, user)
                    cursor.execute(stmt, data)
            except Exception as e:
                self.__parent.rollback()
                return ActionResult(error_message="Failed to log usage of item", exception=e)


            # If all went well, commit the changes
            self.__parent.commit()
            return ActionResult(success=True)



        def add_recipe(self, 
                       recipe_name:str, 
                       ingredients:list[tuple[str, float]]
                       ) -> ActionResult:
            """
            Adds a recipe to the database.

            Parameters
            ----------
            `recipe_name` : str
                The name of the recipe to add.

            `ingredients` : list[[tuple[[str, float]]]]
                The list of ingredients required by the recipe.
                Each ingredient in this list is a tuple with the first 
                value being the name of the ingredient and the second 
                being the quantity of that ingredient required by the 
                recipe.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            self.__parent.start_transaction()

            try:
                stmt_template = self.__parent._Database__sql_statements.get_query(group="Template", name="Create template")
                template_data = (recipe_name,)
                cursor.execute(stmt_template, template_data)

                stmt_recipe = self.__parent._Database__sql_statements.get_query(group="Recipe", name="Create recipe")
                recipe_data = (recipe_name,)
                cursor.execute(stmt_recipe, recipe_data)

                stmt_ingredients = self.__parent._Database__sql_statements.get_query(group="Ingredients", name="Add ingredient")
                ri_tuples = []
                for i in ingredients:
                    ri_tuples.append((recipe_name, *i))
                cursor.executemany(stmt_ingredients, ri_tuples)
            except Exception as e:
                self.__parent.rollback()
                return ActionResult(error_message="Failed to create recipe", exception=e)

            self.__parent.commit()
            return ActionResult(success=True)



        def gen_shopping_list(self, timestamp:dt.datetime=dt.datetime.now() + dt.timedelta(days=7)) -> ActionResult:
            """
            Generates a Shopping list from the items that will be needed 
            for planned meals within the period from now until the provided
            `timestamp` and that there currently is not enough of in inventory.

            Parameters
            ----------
            `timestamp` : datetime
                The upper bound timestamp for meals to gather out of stock items 
                for to populate the shopping list out of.
                Defaults to now plus seven days.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            try:
                statement = self.__parent._Database__sql_statements.get_query(group="Shopping List", name="Select missing ingredients")
                data = (timestamp, timestamp)
                cursor.execute(statement, data)
                return ActionResult(data=cursor.fetchall())
            except Exception as e:
                return ActionResult(error_message="Failed to generate shopping list", exception=e)



        # ----- PURCHASE -----

        def purchase_item(self,
                          item_name:str,
                          quantity:float,
                          price:float,
                          store:str,
                          parent_name:str,
                          storage_location:str,
                          expiry:dt.datetime|None=None
                          ) -> ActionResult:
            """
            Purchases an item and adds it to the inventory.

            Parameters
            ----------
            `item_name` : str
                The name of the item that was purchased.

            `quantity` : float
                The quantity of the item that was purchased.

            `price` : float
                The price that this item cost.
                This is the price for the whole item, not per unit integer.

            `store` : str
                The name of the store the item was bought at.

            `parent_name` : str
                The name of the parent user who bought the item.

            `storage_location` : str
                The name of the storage location to store the item at
                in inventory.

            `expiry` : datetime | None
                The expiry date of the item.
                `None` if the item does not have an expiry date.
            """
            cursor:MySQLCursorDict = self.__parent._Database__cursor

            # Check quantity is greater than 0
            if quantity <= 0:
                return ActionResult(error_message="Quantity for a purchase cannot be less than 0")

            # Start a database transaction
            self.__parent.start_transaction()            

            # Create purchase record
            try:
                statement = self.__parent._Database__sql_statements.get_query(group="Purchase", name="Add purchase record")
                data = (item_name, quantity, price, store, parent_name)
                cursor.execute(statement, data)
            except Exception as e:
                self.__parent.rollback()
                return ActionResult(error_message="Failed to add purchase record", exception=e)


            # Add item to inventory
            add_item_to_inv_result = self._add_item_to_inventory(item_name=item_name, storage_name=storage_location, expiry=expiry, quantity=quantity)
            if not add_item_to_inv_result.is_success():
                self.__parent.rollback()
                return add_item_to_inv_result

            # Commit the changes if we successfully made it to this point
            self.__parent.commit()
            return ActionResult(success=True)


