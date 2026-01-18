from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.exc import SQLAlchemyError
from app.extensions.db import db

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository with safe CRUD helpers.
    """

    model: Type[ModelType]

    @classmethod
    def get_by_id(cls, record_id: int) -> Optional[ModelType]:
        if record_id <= 0:
            return None

        try:
            return db.session.get(cls.model, record_id)
        except SQLAlchemyError:
            db.session.rollback()
            return None

    @classmethod
    def list_all(cls) -> List[ModelType]:
        try:
            return cls.model.query.all()    # type: ignore
        except SQLAlchemyError:
            return []

    @classmethod
    def save(cls, instance: ModelType) -> bool:
        try:
            db.session.add(instance)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @classmethod
    def delete(cls, instance: ModelType) -> bool:
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False
