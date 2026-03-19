from typing import List
from sqlalchemy.orm import Session
from ._base_repository import BaseRepository
from ..model.db.gps_track import GPSTrack


class GPSTrackRepository(BaseRepository[GPSTrack]):
    def __init__(self, session: Session):
        super().__init__(session, GPSTrack)

    def find_by_device_id(self, device_id: int) -> List[GPSTrack]:
        return self.session.query(GPSTrack).filter(GPSTrack.device_id == device_id).order_by(GPSTrack.timestamp).all()

    def find_latest_by_device(self, device_id: int) -> GPSTrack:
        return self.session.query(GPSTrack).filter(GPSTrack.device_id == device_id).order_by(GPSTrack.timestamp.desc()).first()
