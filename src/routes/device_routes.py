from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..datalayer.database import get_db
from ..datalayer.repository.device_repository import DeviceRepository
from ..datalayer.model.db.device import Device

router = APIRouter(prefix="/api", tags=["Devices"])


@router.post("/device")
async def create_device(name: str, color: str = "#FF0000", db: Session = Depends(get_db)):
    device_repo = DeviceRepository(db)
    device = Device(name=name, color=color)
    saved_device = device_repo.save(device)
    return {"id": saved_device.id, "name": saved_device.name, "color": saved_device.color}


@router.get("/devices")
async def get_devices(db: Session = Depends(get_db)):
    device_repo = DeviceRepository(db)
    devices = device_repo.get_all()
    return [{"id": d.id, "name": d.name, "color": d.color} for d in devices]
