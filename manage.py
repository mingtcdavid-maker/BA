import sys
from database import createbatable

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "createtable":
        print("Usage: python3 manage.py createtable <table_name>")
        return
    createbatable(sys.argv[2]) #use python3 manage.py createtable (tablename) to create a table in database


if __name__ == "__main__":
    main()
