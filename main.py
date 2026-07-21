from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from io import BytesIO
from models import BacylinderUpdate, Bacylinder, PendingRequestCreate
from database import (
    createbatable, list_ba, querytable, query_all, create_ba, update_ba,
    creatependingtable, creatependingba, getpending, list_pending, acceptpending, delete_ba, delete_pending
)
# collumns for sql table "logs" in logs.db
# serial,
# location,
# next_hydrostatic_date,
# last_servicing_date,
# date_of_expiry,
# manufacture_date,
# remarks


TABLENAME = "logs" #currently hardcoding a table to be used, logs for all fastapi testing
PENDINGTABLE = "PENDING"

#/api/cylinder to be used for ba dashboard
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
createbatable(TABLENAME)
creatependingtable(PENDINGTABLE)

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post('/api/cylinder', status_code=201)
def createba(ba: Bacylinder):
    if querytable(TABLENAME, "serial", ba.serial) is not None:
        raise HTTPException(400, f"Cylinder with serial {ba.serial} already exists")
    create_ba(TABLENAME, ba)
    return ba


@app.get('/api/cylinder')
def getba(
    cylinder_serial: str = None,
    location: str = None,
    manufacture_date: str = None,
    next_hydrostatic_date: str = None,
    date_of_expiry: str = None,
    last_servicing_date: str = None
    ):
    if cylinder_serial:
        cylinder = querytable(TABLENAME, "serial", cylinder_serial)
        if cylinder is None:
            raise HTTPException(404, "Item not found")
        return cylinder

    if location:
        result = query_all(TABLENAME, "location", location)
        if not result:
            raise HTTPException(404, "Item not found")
        return result

    if manufacture_date:
        result = query_all(TABLENAME, "manufacture_date", manufacture_date)
        if not result:
            raise HTTPException(404, "Item not found")
        return result

    if next_hydrostatic_date:
        result = query_all(TABLENAME, "next_hydrostatic_date", next_hydrostatic_date)
        if not result:
            raise HTTPException(404, "Item not found")
        return result

    if date_of_expiry:
        result = query_all(TABLENAME, "date_of_expiry", date_of_expiry)
        if not result:
            raise HTTPException(404, "Item not found")
        return result

    if last_servicing_date:
        result = query_all(TABLENAME, "last_servicing_date", last_servicing_date)
        if not result:
            raise HTTPException(404, "Item not found")
        return result

    return list_ba(TABLENAME)


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
    for cylinder in list_ba(TABLENAME):
        row = cylinder.model_dump()
        ws.append([row.get(col, "") for col in EXPORT_COLUMNS])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ba_cylinders.xlsx"},
    )


@app.patch('/api/cylinder/{serial}')
def updateba(serial: str, updatedba: BacylinderUpdate):
    if querytable(TABLENAME, "serial", serial) is None:
        raise HTTPException(404, "Item not found")
    update_ba(TABLENAME, updatedba, serial)
    return querytable(TABLENAME, "serial", serial)

@app.delete('/api/cylinder/{serial}')
def deleteba(serial:str):
    if querytable(TABLENAME, "serial", serial) is None:
        raise HTTPException(404, "Item not found")
    delete_ba(TABLENAME, serial)
    delete_pending(PENDINGTABLE, serial) #drop any outstanding NFC request so it doesn't reference a deleted cylinder
    return serial

#end

#/mobile/cylinder to be used for the mobile app
#use the get route /api/cylinder?cylinder_serial={serial} for mobile get also

@app.post('/mobile/cylinder/{serial}', status_code=201)
def create_pending(serial: str, request: PendingRequestCreate):
    if querytable(TABLENAME, "serial", serial) is None:
        raise HTTPException(404, f"No cylinder with serial {serial}")
    creatependingba(PENDINGTABLE, serial, request.location, request.remarks)
    return {"serial": serial, "location": request.location, "remarks": request.remarks}


#a tapped NFC tag opens a URL in the phone's browser, which is always a GET -
#so the tag must land on this page, whose JS then POSTs to /mobile/cylinder/{serial}
@app.get('/mobile/{serial}')
def mobile_page(serial: str):
    return FileResponse("static/mobile.html")

@app.get('/mobile')
def mobile_page_blank():
    return FileResponse("static/mobile.html")
#end


#/api/pending and /api/accept for managing pending requests on the dashboard

@app.get('/api/pending')
def get_all_pending():
    return list_pending(PENDINGTABLE)

@app.get('/api/pending/{serial}')
def get_pending(serial: str):
    result = getpending(PENDINGTABLE, serial)
    if result is None:
        raise HTTPException(404, "Item not found")
    else:
        return result


@app.post('/api/accept/{serial}')
def accept_pending(serial: str, status: bool):
    result = acceptpending(TABLENAME, PENDINGTABLE, serial, status) #if status True, accept, if status False, reject
    if result is None:
        raise HTTPException(404, "No pending request for this serial")
    return {"serial": serial, "accepted": status}
