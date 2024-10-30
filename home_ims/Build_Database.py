# Build Database Script

import mysql.connector
from mysql.connector import Error
from sql_statements import *

# Connect to database
def connect(db_name=str):
    connection = None
    try:
        # Not sure if this is correct...
        connection = mysql.connector.connect(
            host='localhost', # I think we are using local host?
            user='TBD',
            password='TBD',
            database=db_name
        )
        if db_name:
            print(f"Connected to \"{db_name}\".")
        else:
            print("Connected to MariaDB.")
    except Error as e:
        print(e)
    
    return connection

# Create database
# Change MariaDB database to be stored in project folder
def create_db(connection, db_name=str):
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE %s;", db_name)
    except Error as e:
        print(e)

# Execute an SQL statement on the connected database
# I think this function would work for all SQL queries?
def exec_sql(connection, sql_statement=str):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_statement)
    except Error as e:
        print(e)

# Main
if __name__ == "__main__":
    db_name = "HomeIMS"
    connection = connect()
    
    if connection:
        create_db(connection, db_name)
        connection.close()

        connection = connect(db_name)
        if connection:
            # Loop through the SQL statements for creating tables
            for i in sql_tables:
                exec_sql(connection, sql_tables[i])
                # Print statements for debugging
                command = sql_tables.split()[:3]
                print(f"Success:    {command}")
            connection.close()

    else:
        print(f"Connection failed, database {db_name} not created.")

