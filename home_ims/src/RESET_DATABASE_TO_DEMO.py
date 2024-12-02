from Database import Database

mydb = Database()
mydb.connect()
mydb.build_demo_database()
mydb.close()
