from typing import TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self) -> List[T]:
        return self.session.query(self.model_class).all()

    def save(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete_by_id(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
