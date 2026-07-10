from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import Optional

filename = "logs.json"


with open(filename, "r") as f:
    list = json.load(f)



class Bacylinder(BaseModel): # base model used for creating ba objects
    serial: str = None
    location: str = None
    next_hydrostatic_date: str = None
    manufacture_date: str = None


class BacylinderUpdate(BaseModel): #updater model for updating using patch
    serial: Optional[str] = None
    location: Optional[str] = None
    next_hydrostatic_date: Optional[str] = None
    manufacture_date: Optional[str] = None

app = FastAPI()

@app.get("/")
def root():
    return list


@app.post('/ba')
def createba(ba: Bacylinder):
    list.append(ba.model_dump())
    with open(filename, "w") as f:
        json.dump(list, f, indent=4)
    return list

@app.get('/ba')
def getba(
    item_id: int = None,
    cylinder_serial: str = None,
    location: str = None,
    manufacture_date: str = None,
    next_hydrostatic_date: str = None,
    ):
    if item_id:
        return list[item_id]
    elif cylinder_serial:
        for cylinder in list:
            if cylinder["serial"] == cylinder_serial:
                return cylinder
            else: 
                HTTPException(404, "Item not found")
    elif location:
        for cylinder in list:
            if cylinder["location"] == location:
                return cylinder
            else:
                HTTPException(404, "Item not found")
    #add manu date and hydro date


@app.patch('/ba{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    for ba in list:
        if ba["serial"] == serial:

            ba_to_update: dict = ba # this is the dictionary containing serial, location etc inside of list
            list.remove(ba)

    update_data = updatedba.model_dump(exclude_unset = True) #this is the updated informatin in a dictionary
    ba_to_update.update(update_data)
    list.append(ba_to_update)
    with open(filename, "w") as f:
        json.dump(list, f, indent=4)
    return list


    

    


@app.get('/test')
def gettest():
    return f