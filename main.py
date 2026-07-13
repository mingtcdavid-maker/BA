from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openpyxl import Workbook
from io import BytesIO
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
    last_servicing_date: str
    date_of_expiry: str
    remarks: str



class BacylinderUpdate(BaseModel): #updater model for updating using patch
    serial: Optional[str] = None
    location: Optional[str] = None
    next_hydrostatic_date: Optional[str] = None
    manufacture_date: Optional[str] = None
    last_servicing_date: Optional[str] = None
    date_of_expiry: Optional[str] = None
    remarks: Optional[str] = None


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
        result = [c for c in cylinders if c["manufacture_date"] == manufacture_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if next_hydrostatic_date:
        result = [c for c in cylinders if c["next_hydrostatic_date"] == next_hydrostatic_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if last_servicing_date:
        result = [c for c in cylinders if c["last_servicing_date"] == last_servicing_date]
        if result:
            return result
        raise HTTPException(404, "Item not found")
    if date_of_expiry:
        result = [c for c in cylinders if c["date_of_expiry"] == date_of_expiry]
        if result:
            return result
        raise HTTPException(404, "Item not found")

    return cylinders
    


EXPORT_COLUMNS = [
    "serial",
    "location",
    "manufacture_date",
    "next_hydrostatic_date",
    "last_servicing_date",
    "date_of_expiry",
    "remarks",
]
EXPORT_HEADERS = [
    "Serial",
    "Appliance",
    "Manufacture date",
    "Next hydrostatic test",
    "Last servicing date",
    "Date of expiry",
    "Remarks",
]


@app.get('/export')
def export_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "BA Cylinders"
    ws.append(EXPORT_HEADERS)
    for c in cylinders:
        ws.append([c.get(col, "") for col in EXPORT_COLUMNS])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ba_cylinders.xlsx"},
    )


@app.patch('/ba/{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    for ba in cylinders:
        if ba["serial"] == serial:
            update_data = updatedba.model_dump(exclude_unset=True)
            ba.update(update_data)
            save()
            return ba
    raise HTTPException(404, "Item not found")
