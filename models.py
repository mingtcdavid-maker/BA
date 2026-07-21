from pydantic import BaseModel
from typing import Optional, List

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


class PendingRequestCreate(BaseModel): # body for /mobile/cylinder/{serial}
    location: str
    remarks: Optional[str] = None


class BatchPendingRequestCreate(BaseModel): # body for /mobile/batch
    serials: List[str]
    location: str
    remarks: Optional[str] = None