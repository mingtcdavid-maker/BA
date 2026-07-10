from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import Optional

filename = "logs.json"


with open(filename, "r") as f:
    cylinders = json.load(f)


class Bacylinder(BaseModel): # base model used for creating ba objects
    serial: str
    location: str
    next_hydrostatic_date: str
    manufacture_date: str


class BacylinderUpdate(BaseModel): #updater model for updating using patch
    serial: Optional[str] = None
    location: Optional[str] = None
    next_hydrostatic_date: Optional[str] = None
    manufacture_date: Optional[str] = None


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
    if any(c["serial"] == ba.serial for c in cylinders):
        raise HTTPException(400, f"Cylinder with serial {ba.serial} already exists")
    cylinders.append(ba.model_dump())
    save()
    return ba.model_dump()


@app.get('/ba')
def getba(
    item_id: int = None,
    cylinder_serial: str = None,
    location: str = None,
    manufacture_date: str = None,
    next_hydrostatic_date: str = None,
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
    return cylinders
    #add manu date and hydro date


@app.patch('/ba/{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    for ba in cylinders:
        if ba["serial"] == serial:
            update_data = updatedba.model_dump(exclude_unset=True)
            ba.update(update_data)
            save()
            return ba
    raise HTTPException(404, "Item not found")
