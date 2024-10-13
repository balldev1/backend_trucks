from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# รถ
class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, index=True)
    truck_type = Column(String)
    queue_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="waiting")

# ประตู
class Gate(Base):
    __tablename__ = "gates"

    id = Column(Integer, primary_key=True, index=True)
    gate_type = Column(String)
    capacity = Column(Integer)
    current_queue = Column(Integer, default=0)

# คิว
class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"))
    gate_id = Column(Integer, ForeignKey("gates.id"))
    queue_status = Column(String, default="waiting")
    truck = relationship("Truck")
    gate = relationship("Gate")

# แจ้งเตือน
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id"))
    notification_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    queue = relationship("Queue")
