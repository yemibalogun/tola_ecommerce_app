from typing import Optional
from app.repositories.base import BaseRepository
from app.models.tenant import Tenant


class TenantRepository(BaseRepository[Tenant]):
    model = Tenant

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Tenant]:
        if not slug:
            return None

        return Tenant.query.filter_by(slug=slug).first()
