import sqlite3
from models import Bacylinder, BacylinderUpdate
import sys

DATABASE = "logs.db" #constant name of the database file 



def getconnection(): #creates the conn
    return sqlite3.connect(DATABASE)

def createbatable(table_name: str): 
    conn = getconnection()
    c=conn.cursor()
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    serial text PRIMARY KEY,
    location text,
    next_hydrostatic_date text,
    last_servicing_date text,
    date_of_expiry text,
    manufacture_date text,
    remarks text
    )
    """
    c.execute(sql)
    conn.commit()
    conn.close()

def querytable(table_name: str, parameter_to_be_queried: str, parameter: str):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c=conn.cursor()
    sql = f"SELECT * FROM {table_name} WHERE {parameter_to_be_queried} = ?"
    c.execute(sql, (parameter,))
    row = c.fetchone()
    conn.close()
    if row == None:
        return None
    else:
        cylinder = Bacylinder.model_validate(dict(row))
        return cylinder

def create_ba(table_name: str, ba_object: Bacylinder):
    conn = getconnection()
    c=conn.cursor()
    sql = f"""
    INSERT INTO {table_name} 
    (
    serial,
    location,
    next_hydrostatic_date,
    last_servicing_date,
    date_of_expiry,
    manufacture_date,
    remarks
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    c.execute(
        sql,
        (
            ba_object.serial,
            ba_object.location,
            ba_object.next_hydrostatic_date,
            ba_object.last_servicing_date,
            ba_object.date_of_expiry,
            ba_object.manufacture_date,
            ba_object.remarks
        )
    )  
    conn.commit()
    conn.close()

def update_ba(table_name: str, ba_update_object: BacylinderUpdate, serial: str):
    conn = getconnection()
    c = conn.cursor()
    for key, value in ba_update_object.model_dump(exclude_none=True).items():
        sql = f"UPDATE {table_name} SET {key} = ? WHERE serial = ?"
        c.execute(
            sql, (value, serial)
        )
        
    conn.commit()
    conn.close()


