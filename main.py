from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import Optional
from models import BacylinderUpdate, Bacylinder
from database import createbatable, querytable, create_ba, update_ba
# collumns for sql table "logs" in logs.db
# serial,
# location,
# next_hydrostatic_date,
# last_servicing_date,
# date_of_expiry,
# manufacture_date,
# remarks


TABLENAME = "logs" #currently hardcoding a table to be used, logs for all fastapi testing


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post('/ba', status_code=201)
def createba(ba: Bacylinder):
    create_ba(TABLENAME, ba)




@app.get('/ba')
def getba(
    cylinder_serial: str = None,
    location: str = None,
    manufacture_date: str = None,
    next_hydrostatic_date: str = None,
    date_of_expiry: str = None,
    last_servicing_date = None
    ):
    if cylinder_serial:
        querytable(TABLENAME, "serial", cylinder_serial)
        
    if location:
        querytable(TABLENAME, "location", location)

    if manufacture_date:
        querytable(TABLENAME, "manufacture_date", manufacture_date)

    if next_hydrostatic_date:
        querytable(TABLENAME, "next_hydrostatic_date", next_hydrostatic_date)

    if date_of_expiry:
        querytable(TABLENAME, "date_of_expiry", date_of_expiry)

    if last_servicing_date:
        querytable(TABLENAME, "last_servicing_date", last_servicing_date)

    


@app.patch('/ba/{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    update_ba(TABLENAME, updatedba, serial)



