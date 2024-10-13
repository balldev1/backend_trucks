from pydantic import BaseModel
from datetime import datetime

class TruckBase(BaseModel):
    license_plate: str
    truck_type: str

class TruckCreate(TruckBase):
    pass

class Truck(TruckBase):
    id: int
    queue_time: datetime
    status: str

    class Config:
        orm_mode = True

class GateBase(BaseModel):
    gate_type: str
    capacity: int

class GateCreate(GateBase):
    pass

class Gate(GateBase):
    id: int
    current_queue: int

    class Config:
        orm_mode = True

class QueueBase(BaseModel):
    truck_id: int
    gate_id: int

class QueueCreate(QueueBase):
    pass

class Queue(QueueBase):
    id: int
    queue_status: str

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    queue_id: int

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    notification_time: datetime
    status: str

    class Config:
        orm_mode = True
