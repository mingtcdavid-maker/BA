from fastapi import FastAPI
from pydantic import BaseModel
import json

filename = "logs.json"


with open(filename, "r") as f:
    list = json.load(f)




class Bacylinder(BaseModel):
    serial: str = None
    location: str = None
    next_hydrostatic_date: str = None
    manufacture_date: str = None

app = FastAPI()

@app.get("/")
def root():
    return list


@app.post('/ba')
def createba(ba: Bacylinder):
    list.append(ba)
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
    elif location:
        for cylinder in list:
            if cylinder["location"] == location:
                return cylinder
    #add manu date and hydro date



@app.get('/test')
def gettest():
    return f