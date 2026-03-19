from sqlalchemy.orm import Session
from ._base_repository import BaseRepository
from ..model.db.device import Device


class DeviceRepository(BaseRepository[Device]):
    def __init__(self, session: Session):
        super().__init__(session, Device)

    def find_by_name(self, name: str) -> Device:
        return self.session.query(Device).filter(Device.name == name).first()
