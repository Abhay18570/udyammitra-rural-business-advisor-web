"""Public catalog reads, independent of the financial and scheme router services."""
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.government_scheme_repository import GovernmentSchemeRepository
from app.schemas.government_scheme import GovernmentSchemeDetail, GovernmentSchemeFilters, GovernmentSchemePage
from app.services.government_scheme_import import ALIASES, compact


class GovernmentSchemeService:
    def __init__(self, db):
        self.repository = GovernmentSchemeRepository(db)

    def _read(self, operation, *args):
        try:
            return operation(*args)
        except SQLAlchemyError:
            # Sanitize even when the application runs with debug enabled.
            raise HTTPException(status_code=503, detail='Government scheme catalog is temporarily unavailable.') from None

    def list(self, filters):
        filters = filters.model_copy()
        filters.search = compact(filters.search or '') or None
        if filters.state is not None:
            value = compact(filters.state)
            filters.state = next((state for state, aliases in ALIASES.items() if value.casefold() in [alias.casefold() for alias in aliases]), value)
        if filters.category is not None:
            filters.category = compact(filters.category)
        items, total = self._read(self.repository.list_schemes, filters)
        return GovernmentSchemePage(items=items, total=total, page=filters.page, page_size=filters.page_size,
                                    total_pages=(total + filters.page_size - 1) // filters.page_size)

    def get(self, slug):
        record = self._read(self.repository.get_scheme_by_slug, slug)
        if record is None:
            raise HTTPException(status_code=404, detail='Government scheme not found.')
        return GovernmentSchemeDetail.model_validate(record)

    def filters(self):
        return GovernmentSchemeFilters(**self._read(self.repository.get_filter_metadata))
