import sqlite3
import os
from models import Bacylinder, BacylinderUpdate

DATABASE = os.environ.get("DATABASE_PATH", "logs.db") #overridden by DATABASE_PATH in containerized/Fly deployments, where it points at the persistent volume mount



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

def list_ba(table_name: str):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    conn.close()
    return [Bacylinder.model_validate(dict(row)) for row in rows]

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

def query_all(table_name: str, parameter_to_be_queried: str, parameter: str):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    sql = f"SELECT * FROM {table_name} WHERE {parameter_to_be_queried} = ?"
    c.execute(sql, (parameter,))
    rows = c.fetchall()
    conn.close()
    return [Bacylinder.model_validate(dict(row)) for row in rows]

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
    for key, value in ba_update_object.model_dump(exclude_unset=True).items():
        sql = f"UPDATE {table_name} SET {key} = ? WHERE serial = ?"
        c.execute(
            sql, (value, serial)
        )

    conn.commit()
    conn.close()

def delete_ba(table_name:str, serial:str):
    conn = getconnection()
    c = conn.cursor()
    sql = f"""
    DELETE FROM {table_name} WHERE serial = ?
    """
    c.execute(sql, (serial,))
    conn.commit()
    conn.close()
    return serial

def delete_pending(table_name: str, serial: str):
    conn = getconnection()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name} WHERE serial = ?", (serial,))
    conn.commit()
    conn.close()


def creatependingtable(table_name: str):
    conn = getconnection()
    c = conn.cursor()
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

def list_pending(table_name: str):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def creatependingba(table_name: str, serial: str, new_location: str, remarks: str = None):
    conn = getconnection()
    c = conn.cursor()
    #re-scanning the same tag replaces its previous pending request rather than erroring
    sql = f"""
    INSERT INTO {table_name} (serial, location, remarks)
    VALUES (?, ?, ?)
    ON CONFLICT(serial) DO UPDATE SET location = excluded.location, remarks = excluded.remarks
    """
    c.execute(sql, (serial, new_location, remarks))
    conn.commit()
    conn.close()

def getpending(table_name: str, serial:str):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c=conn.cursor()
    sql = f"SELECT * FROM {table_name} WHERE serial = ?"
    c.execute(sql, (serial,))
    row = c.fetchone()
    conn.close()
    if row == None:
        return None
    else:
        return dict(row)

def acceptpending(cylinder_table: str, pending_table: str, serial: str, status: bool):
    conn = getconnection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(f"SELECT * FROM {pending_table} WHERE serial = ?", (serial,))
    row = c.fetchone()
    if row is None:
        conn.close()
        return None
    pending = dict(row)
    if status: #accept: apply the requested location to the cylinder
        c.execute(f"UPDATE {cylinder_table} SET location = ? WHERE serial = ?", (pending["location"], serial))
    c.execute(f"DELETE FROM {pending_table} WHERE serial = ?", (serial,))
    conn.commit()
    conn.close()
    return pending
