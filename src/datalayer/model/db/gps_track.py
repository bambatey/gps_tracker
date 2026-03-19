from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base


class GPSTrack(Base):
    __tablename__ = "gps_tracks"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="tracks")
