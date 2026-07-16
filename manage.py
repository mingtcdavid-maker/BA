import sys
from database import createbatable, creatependingtable

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("createtable", "createpending"):
        print("Usage: python3 manage.py createtable <table_name>")
        print("       python3 manage.py createpending")
        return
    if sys.argv[1] == "createtable":
        if len(sys.argv) < 3:
            print("Usage: python3 manage.py createtable <table_name>")
            return
        createbatable(sys.argv[2]) #use python3 manage.py createtable (tablename) to create a table in database
        print(f"Table '{sys.argv[2]}' ready.")
    elif sys.argv[1] == "createpending":
        creatependingtable("PENDING")
        print("Table 'PENDING' ready.")


if __name__ == "__main__":
    main()
