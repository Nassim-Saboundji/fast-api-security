from database import Database

# Run this file once to create the required table inside your postgres database.
db = Database()

db.exec(""" 
CREATE TABLE users(
    username VARCHAR PRIMARY KEY,
    password bytea
)
""",())

db.close()



