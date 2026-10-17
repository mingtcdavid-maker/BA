import sys
from database import createbatable, creatependingtable, set_station

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("createtable", "createpending", "setstation"):
        print("Usage: python3 manage.py createtable <table_name>")
        print("       python3 manage.py createpending")
        print("       python3 manage.py setstation <table_name> <serial> <station>")
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
    elif sys.argv[1] == "setstation":
        #admin-only: backfills/corrects station directly in the db, bypassing the API since station is not editable there
        if len(sys.argv) < 5:
            print("Usage: python3 manage.py setstation <table_name> <serial> <station>")
            return
        set_station(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Set station '{sys.argv[4]}' for serial '{sys.argv[3]}' in table '{sys.argv[2]}'.")


if __name__ == "__main__":
    main()
