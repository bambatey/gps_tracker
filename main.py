from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import asyncio
from config import DATABASE_URL
import os

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database models
class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String, default="#FF0000")
    created_at = Column(DateTime, default=datetime.utcnow)

    tracks = relationship("GPSTrack", back_populates="device", cascade="all, delete-orphan")

class GPSTrack(Base):
    __tablename__ = "gps_tracks"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="tracks")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Routes
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/track")
async def track():
    return FileResponse("static/tracker.html")

@app.post("/api/device")
async def create_device(name: str, color: str = "#FF0000"):
    db = SessionLocal()
    device = Device(name=name, color=color)
    db.add(device)
    db.commit()
    db.refresh(device)
    db.close()
    return {"id": device.id, "name": device.name, "color": device.color}

@app.get("/api/devices")
async def get_devices():
    db = SessionLocal()
    devices = db.query(Device).all()
    db.close()
    return [{"id": d.id, "name": d.name, "color": d.color} for d in devices]

@app.get("/api/device/{device_id}/tracks")
async def get_device_tracks(device_id: int):
    db = SessionLocal()
    tracks = db.query(GPSTrack).filter(GPSTrack.device_id == device_id).order_by(GPSTrack.timestamp).all()
    db.close()

    return [
        {
            "latitude": t.latitude,
            "longitude": t.longitude,
            "accuracy": t.accuracy,
            "timestamp": t.timestamp.isoformat()
        }
        for t in tracks
    ]

@app.get("/api/export/gpx/{device_id}")
async def export_gpx(device_id: int):
    db = SessionLocal()
    device = db.query(Device).filter(Device.id == device_id).first()
    tracks = db.query(GPSTrack).filter(GPSTrack.device_id == device_id).order_by(GPSTrack.timestamp).all()
    db.close()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    gpx_content = generate_gpx(device, tracks)
    return FileResponse(
        path="temp.gpx",
        media_type="application/gpx+xml",
        filename=f"{device.name}.gpx"
    )

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: int):
    await manager.connect(websocket)
    db = SessionLocal()

    try:
        # device_id=0 means listen-only (for map viewers)
        if device_id == 0:
            while True:
                # Keep connection alive (listen only)
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=30)
                except asyncio.TimeoutError:
                    pass
        else:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                await websocket.close(code=1000)
                return

            while True:
                data = await websocket.receive_json()

                # Save GPS track
                track = GPSTrack(
                    device_id=device_id,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    accuracy=data.get("accuracy")
                )
                db.add(track)
                db.commit()

                # Broadcast to all connected clients
                await manager.broadcast({
                    "type": "location_update",
                    "device_id": device_id,
                    "device_name": device.name,
                    "device_color": device.color,
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "accuracy": data.get("accuracy"),
                    "timestamp": track.timestamp.isoformat()
                })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)
        db.close()

def generate_gpx(device, tracks):
    gpx = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>{}</name>
  </metadata>
  <trk>
    <name>{}</name>
    <trkseg>
'''.format(device.name, device.name)

    for track in tracks:
        gpx += '''      <trkpt lat="{}" lon="{}">
        <time>{}</time>
      </trkpt>
'''.format(track.latitude, track.longitude, track.timestamp.isoformat())

    gpx += '''    </trkseg>
  </trk>
</gpx>'''

    with open("temp.gpx", "w") as f:
        f.write(gpx)

    return gpx

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
