from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import Optional
from models import BacylinderUpdate, Bacylinder
from database import createbatable, querytable, create_ba, update_ba






filename = "logs.json"


with open(filename, "r") as f:
    cylinders = json.load(f)



def save():
    with open(filename, "w") as f:
        json.dump(cylinders, f, indent=4)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post('/ba', status_code=201)
def createba(ba: Bacylinder):
    create_ba()




@app.get('/ba')
def getba(
    item_id: int = None,
    cylinder_serial: str = None,
    location: str = None,
    manufacture_date: str = None,
    next_hydrostatic_date: str = None,
    date_of_expiry: str = None,
    last_servicing_date = None
    ):
    if item_id is not None:
        if 0 <= item_id < len(cylinders):
            return cylinders[item_id]
        raise HTTPException(404, "Item not found")
    if cylinder_serial:
        for cylinder in cylinders:
            if cylinder["serial"] == cylinder_serial:
                return cylinder
        raise HTTPException(404, "Item not found")
    if location:
        result = [c for c in cylinders if c["location"] == location]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if manufacture_date:
        result = [c for c in cylinder if c["manufacture_date"] == manufacture_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if next_hydrostatic_date:
        result = [c for c in cylinder if c["next_hydrostatic_date"] == next_hydrostatic_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if last_servicing_date:
        result = [c for c in cylinder if c["last_servicing_date"] == last_servicing_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if date_of_expiry:
        result = [c for c in cylinder if c["date_of_expiry"] == date_of_expiry]
        if result:
            return result
        raise HTTPException(404, "Item not found")

    return cylinders
    


@app.patch('/ba/{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    for ba in cylinders:
        if ba["serial"] == serial:
            update_data = updatedba.model_dump(exclude_unset=True)
            ba.update(update_data)
            save()
            return ba
    raise HTTPException(404, "Item not found")
