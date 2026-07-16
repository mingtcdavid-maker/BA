import sys
from database import createbatable, getconnection
import sqlite3

def main():
    if sys.argv[1] != "createtable" or sys.argv[1] != "createpending":
        print("Usage: python3 manage.py createtable <table_name>")
        return
    if sys.argv[1] == "createtable":
        createbatable(sys.argv[2]) #use python3 manage.py createtable (tablename) to create a table in database
    elif sys.argv[1] == "createpending":
        create_pending_table("PENDING")

def create_pending_table(table_name: str): 
    conn = getconnection()
    c=conn.cursor()
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    serial text PRIMARY KEY,
    location text,
    remarks text
    )
    """
    c.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
