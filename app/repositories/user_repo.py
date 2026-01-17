from typing import Optional
from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    model = User

    @staticmethod
    def get_by_email(email: str, tenant_id: int) -> Optional[User]:
        if not email or tenant_id <= 0:
            return None

        return (
            User.query
            .filter_by(email=email, tenant_id=tenant_id)
            .first()
        )
