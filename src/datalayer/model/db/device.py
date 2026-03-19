from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String, default="#FF0000")
    created_at = Column(DateTime, default=datetime.utcnow)

    tracks = relationship("GPSTrack", back_populates="device", cascade="all, delete-orphan")
