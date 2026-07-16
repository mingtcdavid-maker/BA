from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from io import BytesIO
from models import BacylinderUpdate, Bacylinder
from database import createbatable, list_ba, querytable, query_all, create_ba, update_ba, creatependingba, getpending, acceptpending
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


#end

#/mobile/cylinder to be used for the mobile app
#use the get route /api/cylinder/{serial} for mobile get also

@app.post('/mobile/cylinder/{serial}')
def create_pending(serial:str, new_location:str):
    try:
        creatependingba(serial, new_location)
        return "Successfully created pending reqeust"
    except:
        return "failed to create pending reqeust"


#create a html for a mobile website
@app.get('/mobile')
def mobile():
    ...
#end


#/api/updates for managing pending

@app.get('/api/pending/{serial}')
def get_pending(serial:str):
    result = getpending(PENDINGTABLE, serial)
    if result is None:
        raise HTTPException(404, "Item not found")
    else: 
        return result
    

@app.post('/api/accept/{serial}')
def accept_pending(serial:str, status:bool):
    acceptpending(serial, status) #if status True, accept, if status False, reject
    