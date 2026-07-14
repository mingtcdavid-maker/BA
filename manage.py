import sqlite3
from database import createbatable, DATABASE, getconnection
import sys

database = DATABASE

def main():
    if sys.argv[1] == "createtable": #use python3 manage.py createtable (tablename) to create a table in database
        createbatable(sys.argv[2])


if __name__ == "__main__":
    main()

    