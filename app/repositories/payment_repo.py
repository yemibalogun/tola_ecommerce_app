from typing import Optional
from app.repositories.base import BaseRepository
from app.models.payment import Payment


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    @staticmethod
    def get_by_reference(reference: str) -> Optional[Payment]:
        if not reference:
            return None

        return Payment.query.filter_by(reference=reference).first()
