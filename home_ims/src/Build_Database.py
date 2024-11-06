# Build Database Script

# -- Library Imports --
import mysql.connector
from mysql.connector import Error

# -- Local Imports --
from env import MARIADB_HOST, MARIADB_PORT, MARIADB_DATABASE_NAME, MARIADB_USER
from secrets import MARIADB_PASSWORD # (ignore error, it's caused by .gitignore file and is expected.)
from sql_statements import *



class Build_Database:


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

        self.__connection = None;
        self.__cursor = None;



    # Connect to database
    # Creates a connection and a cursor
    def __connect(self) -> bool:

        # Used to record the status of the operation.
        connection_success:bool = True

        # Try to connect to the database.
        try:
            self.__connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )

        except Error as e:
            print("Failed to connect to database")
            print(e)
            self.__connection = None
            connection_success = False

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


        

    # Closes cursor and connection to the database.
    def __close_connection(self) -> None:
        # Close cursor.
        if self.__cursor is not None:
            self.__cursor.close()

        # Close connection.
        if self.__connection is not None:
            self.__connection.close()




    # Create database
    def __create_db(self) -> bool:

        # Used to record the status of the operation.
        operation_successful:bool = True

        # Try to create the database.
        if self.__cursor is not None:
            try:
                self.__cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name};")
            except Error as e:
                print(e)
                operation_successful = False # Record failure.
        
        else:
            operation_successful = False # Record failure.
            if self.__connection is None:
                print("Could not create database. Connection and cursor not established.")
            else:
                print("Could not create database. Connection not established.")

        # Return success status.
        return operation_successful




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

        # Connect to the database
        operation_successful = self.__connect() and operation_successful

        # Create the database and tables.
        if self.__connection:
            operation_successful = self.__create_db() and operation_successful

            # Loop through the SQL statements for creating tables
            for statement in sql_tables:
                operation_successful = self.__exec_sql(statement) and operation_successful
                # Print statements for debugging
                print(f"Success: {statement.split()[:3]}") # TODO Implement proper logging using the logging library

        else:
            operation_successful = False
            print(f"Connection failed, database {self.db_name} not created.")

        # Close the connection to the database
        self.__close_connection()

        # Return the status of building the database
        return operation_successful




