from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# เพิ่มรถเข้าคิว
@app.post("/trucks/", response_model=schemas.Truck)
def create_truck(truck: schemas.TruckCreate, db: Session = Depends(get_db)):
    db_truck = models.Truck(**truck.dict())
    db.add(db_truck)
    db.commit()
    db.refresh(db_truck)
    return db_truck

# สร้างคิว
@app.post("/queues/", response_model=schemas.Queue)
def create_queue(queue: schemas.QueueCreate, db: Session = Depends(get_db)):
    db_queue = models.Queue(**queue.dict())
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue

# เรียกคิวถัดไป
@app.get("/queues/next/")
def get_next_queue(gate_id: int, db: Session = Depends(get_db)):
    queue = db.query(models.Queue).filter_by(gate_id=gate_id, queue_status="waiting").first()
    if not queue:
        raise HTTPException(status_code=404, detail="No queue available")
    queue.queue_status = "in_progress"
    db.commit()
    return queue

# แจ้งเตือนคิวถัดไป
@app.post("/notifications/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification
