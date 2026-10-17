import csv
import sys
from database import createbatable, creatependingtable, set_station, truncate_dates_to_month, import_rows

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("createtable", "createpending", "setstation", "stripdays", "importcsv"):
        print("Usage: python3 manage.py createtable <table_name>")
        print("       python3 manage.py createpending")
        print("       python3 manage.py setstation <table_name> <serial> <station>")
        print("       python3 manage.py stripdays <table_name>")
        print("       python3 manage.py importcsv <table_name> <csv_path> [--replace]")
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
    elif sys.argv[1] == "stripdays":
        #one-time cleanup: drops the day from manufacture/hydro/service/expiry dates, keeping year-month only
        if len(sys.argv) < 3:
            print("Usage: python3 manage.py stripdays <table_name>")
            return
        truncate_dates_to_month(sys.argv[2])
        print(f"Dates truncated to year-month in table '{sys.argv[2]}'.")
    elif sys.argv[1] == "importcsv":
        #bulk-load/replace cylinder rows from a CSV with columns: serial,station,location,next_hydrostatic_date,manufacture_date,last_servicing_date,date_of_expiry,remarks,servicing
        if len(sys.argv) < 4:
            print("Usage: python3 manage.py importcsv <table_name> <csv_path> [--replace]")
            return
        table_name, csv_path = sys.argv[2], sys.argv[3]
        replace_all = "--replace" in sys.argv[4:]
        with open(csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            row["servicing"] = row.get("servicing", "").strip().lower() in ("1", "true", "yes")
        import_rows(table_name, rows, replace_all=replace_all)
        print(f"Imported {len(rows)} row(s) into '{table_name}'" + (" (existing rows replaced first)" if replace_all else " (upserted by serial)") + ".")


if __name__ == "__main__":
    main()
