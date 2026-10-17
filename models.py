from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class Bacylinder(BaseModel): # represents a stored row; station is optional here only so rows created before the column existed still parse
    serial: str
    station: Optional[str] = None
    location: str
    next_hydrostatic_date: str
    manufacture_date: str
    last_servicing_date: str
    date_of_expiry: str
    remarks: str
    servicing: bool = False # true once a user has flagged this overdue cylinder as sent for servicing


class BacylinderCreate(BaseModel): # body for POST /api/cylinder - station is required so no new cylinder is ever created without one
    serial: str
    station: str
    location: str
    next_hydrostatic_date: str
    manufacture_date: str
    last_servicing_date: str
    date_of_expiry: str
    remarks: str



class BacylinderUpdate(BaseModel): #updater model for updating using patch
    model_config = ConfigDict(extra="forbid") # a "station" key in a PATCH body must error, not be silently dropped

    serial: Optional[str] = None
    location: Optional[str] = None
    next_hydrostatic_date: Optional[str] = None
    manufacture_date: Optional[str] = None
    last_servicing_date: Optional[str] = None
    date_of_expiry: Optional[str] = None
    remarks: Optional[str] = None


class PendingRequestCreate(BaseModel): # body for /mobile/cylinder/{serial}
    location: str
    remarks: Optional[str] = None


class BatchPendingRequestCreate(BaseModel): # body for /mobile/batch
    serials: List[str]
    location: str
    remarks: Optional[str] = None