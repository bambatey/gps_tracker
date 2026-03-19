import asyncio
from fastapi import APIRouter, Depends, WebSocket, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..datalayer.database import get_db
from ..datalayer.repository.device_repository import DeviceRepository
from ..datalayer.repository.gps_track_repository import GPSTrackRepository
from ..datalayer.model.db.gps_track import GPSTrack
from ..utils.websocket_manager import ConnectionManager

router = APIRouter(tags=["Tracks"])
manager = ConnectionManager()


@router.get("/api/device/{device_id}/tracks")
async def get_device_tracks(device_id: int, db: Session = Depends(get_db)):
    track_repo = GPSTrackRepository(db)
    tracks = track_repo.find_by_device_id(device_id)
    return [
        {
            "latitude": t.latitude,
            "longitude": t.longitude,
            "accuracy": t.accuracy,
            "timestamp": t.timestamp.isoformat()
        }
        for t in tracks
    ]


@router.get("/api/export/gpx/{device_id}")
async def export_gpx(device_id: int, db: Session = Depends(get_db)):
    device_repo = DeviceRepository(db)
    track_repo = GPSTrackRepository(db)

    device = device_repo.get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    tracks = track_repo.find_by_device_id(device_id)
    gpx_content = _generate_gpx(device, tracks)

    return FileResponse(
        path="temp.gpx",
        media_type="application/gpx+xml",
        filename=f"{device.name}.gpx"
    )


@router.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    device_repo = DeviceRepository(db)
    track_repo = GPSTrackRepository(db)

    try:
        if device_id == 0:
            while True:
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=30)
                except asyncio.TimeoutError:
                    pass
        else:
            device = device_repo.get_by_id(device_id)
            if not device:
                await websocket.close(code=1000)
                return

            while True:
                data = await websocket.receive_json()

                track = GPSTrack(
                    device_id=device_id,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    accuracy=data.get("accuracy")
                )
                saved_track = track_repo.save(track)

                await manager.broadcast({
                    "type": "location_update",
                    "device_id": device_id,
                    "device_name": device.name,
                    "device_color": device.color,
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "accuracy": data.get("accuracy"),
                    "timestamp": saved_track.timestamp.isoformat()
                })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)


def _generate_gpx(device, tracks):
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
