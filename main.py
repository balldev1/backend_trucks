from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
#from starlette.routing import Mount
import socketio

from database import get_db, engine
import models, schemas

models.Base.metadata.create_all(bind=engine)

# สร้าง Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)
socket_app = socketio.ASGIApp(sio)

app = FastAPI()

# กำหนด CORS เพื่อให้การเชื่อมต่อทำงานได้จากไคลเอนต์ต่างๆ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# จัดการการเชื่อมต่อ Socket.IO
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    # ส่งข้อความไปยังทุก client ที่เชื่อมต่อ
    await sio.emit('message', f"Received your message: {data}")

# Mount Socket.IO app เพื่อจัดการการเชื่อมต่อ
app.mount("/socket.io", socket_app)

# เพิ่มรถเข้าคิว
@app.post("/trucks/", response_model=schemas.Truck)
def create_truck(truck: schemas.TruckCreate, db: Session = Depends(get_db)):
    # ตรวจสอบว่าทะเบียนรถมีอยู่ในฐานข้อมูลหรือไม่
    db_truck = db.query(models.Truck).filter(models.Truck.license_plate == truck.license_plate).first()
    if db_truck:
        raise HTTPException(status_code=400, detail="Truck with this license plate already exists.")

    db_truck = models.Truck(**truck.dict())
    db.add(db_truck)
    db.commit()
    db.refresh(db_truck)
    return db_truck

# สร้างคิว
@app.post("/queues/", response_model=schemas.Queue)
def create_queue(queue: schemas.QueueCreate, db: Session = Depends(get_db)):
    # ตรวจสอบว่ารถและประตูมีอยู่ในระบบ
    db_truck = db.query(models.Truck).filter(models.Truck.id == queue.truck_id).first()
    db_gate = db.query(models.Gate).filter(models.Gate.id == queue.gate_id).first()

    if not db_truck:
        raise HTTPException(status_code=404, detail="Truck not found.")
    if not db_gate:
        raise HTTPException(status_code=404, detail="Gate not found.")

    # เพิ่มคิวใหม่
    db_queue = models.Queue(**queue.dict())
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue

# เรียกคิวถัดไป
@app.get("/queues/next/", response_model=schemas.Queue)
def get_next_queue(gate_id: int, db: Session = Depends(get_db)):
    # ค้นหาคิวที่ยังรออยู่สำหรับประตูที่ระบุ
    queue = db.query(models.Queue).filter_by(gate_id=gate_id, queue_status="waiting").first()
    if not queue:
        raise HTTPException(status_code=404, detail="No queue available.")

    # อัปเดตสถานะคิว
    queue.queue_status = "in_progress"
    db.commit()
    return queue

# แจ้งเตือนคิวถัดไป
@app.post("/notifications/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    # ตรวจสอบว่าคิวมีอยู่ในระบบหรือไม่
    db_queue = db.query(models.Queue).filter(models.Queue.id == notification.queue_id).first()
    if not db_queue:
        raise HTTPException(status_code=404, detail="Queue not found.")

    # สร้างการแจ้งเตือนใหม่
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification
