# Build Database Script

import mysql.connector
from mysql.connector import Error
from sql_statements import *




# Connect to database
def connect(db_name:str):
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
def create_db(connection, db_name:str):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    except Error as e:
        print(e)



# Execute an SQL statement on the connected database
# I think this function would work for all SQL queries?
def exec_sql(connection, sql_statement:str):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_statement)
    except Error as e:
        print(e)




def build_database():
    db_name:str = "HomeIMS"
    connection = connect(db_name)
    
    if connection:
        create_db(connection, db_name)

        # Loop through the SQL statements for creating tables
        for action in sql_tables:
            exec_sql(connection, action)
            # Print statements for debugging
            command = action.split()[:3]
            print(f"Success:    {command}")

        connection.close()

    else:
        print(f"Connection failed, database {db_name} not created.")


# Main
if __name__ == "__main__":
    build_database()


