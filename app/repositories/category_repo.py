from typing import Optional
from app.repositories.base import BaseRepository
from app.models.category import Category


class CategoryRepository(BaseRepository[Category]):
    model = Category

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Category]:
        if not slug:
            return None

        return Category.query.filter_by(slug=slug).first()
