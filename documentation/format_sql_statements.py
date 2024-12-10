from home_ims.src.sql_statements import SQL_Statements

SQL_STATEMENTS_FILE_NAME = "Final.sql"

# Create SQL statements object
sql_statements = SQL_Statements()


with open(SQL_STATEMENTS_FILE_NAME, "wt") as file:
    file.write(str(sql_statements))


