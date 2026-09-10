from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.government_scheme import GovernmentScheme, VerificationStatus
from app.schemas.government_scheme import GovernmentSchemeImport


class GovernmentSchemeRepository:
    def __init__(self, db: Session):
        self.db = db

    def import_record(self, data: GovernmentSchemeImport, *, dry_run: bool = False) -> str:
        record = self.db.scalar(select(GovernmentScheme).where(GovernmentScheme.slug == data.slug).with_for_update())
        values = data.model_dump()
        if record is None:
            if not dry_run:
                self.db.add(GovernmentScheme(**values))
            return 'inserted'
        if all(getattr(record, key) == value for key, value in values.items()):
            return 'unchanged'
        # All reviewed states and other datasets are protected, including STALE.
        if (record.verification_status != VerificationStatus.DATASET_ONLY
                or record.source_type != 'DATASET' or record.source_dataset != data.source_dataset):
            return 'conflicts'
        if not dry_run:
            for key, value in values.items():
                setattr(record, key, value)
        return 'updated'


    def list_schemes(self, filters):
        from app.schemas.government_scheme import GovernmentSchemeSort
        model = GovernmentScheme
        predicates = [model.is_active.is_(True)]
        for key in ('level', 'state', 'verification_status'):
            value = getattr(filters, key)
            if value is not None:
                predicates.append(getattr(model, key) == value)
        if filters.state is not None:
            predicates.append(model.level == 'STATE')
        if filters.category is not None:
            predicates.append(model.categories.contains([filters.category]))
        ordering = []
        if filters.search:
            query = func.websearch_to_tsquery('english', filters.search)
            predicates.append(model.search_vector.op('@@')(query))
            ordering.append(func.ts_rank_cd(model.search_vector, query).desc())
        ordering.extend({
            GovernmentSchemeSort.NAME_ASC: [model.scheme_name.asc()],
            GovernmentSchemeSort.NAME_DESC: [model.scheme_name.desc()],
            GovernmentSchemeSort.NEWEST: [model.created_at.desc(), model.scheme_name.asc()],
            GovernmentSchemeSort.OLDEST: [model.created_at.asc(), model.scheme_name.asc()],
        }[filters.sort])
        ordering.append(model.slug.asc())
        total = self.db.scalar(select(func.count()).select_from(model).where(*predicates))
        # Project only lightweight fields; long prose is never fetched into list rows.
        statement = select(
            model.slug, model.scheme_name,
            func.left(func.regexp_replace(model.details, r'\s+', ' ', 'g'), 240).label('short_description'),
            model.level, model.state, model.categories, model.tags,
            model.verification_status, model.source_type,
        ).where(*predicates).order_by(*ordering).limit(filters.page_size).offset((filters.page - 1) * filters.page_size)
        return self.db.execute(statement).mappings().all(), total

    def get_scheme_by_slug(self, slug):
        return self.db.scalar(select(GovernmentScheme).where(
            GovernmentScheme.slug == slug, GovernmentScheme.is_active.is_(True)))

    def get_filter_metadata(self):
        model = GovernmentScheme
        result = {}
        for label, column in [('levels', model.level), ('states', model.state), ('verification_statuses', model.verification_status)]:
            statement = select(column).where(model.is_active.is_(True), column.is_not(None), func.btrim(column) != '').distinct().order_by(column)
            result[label] = list(self.db.scalars(statement))
        expanded = select(func.jsonb_array_elements_text(model.categories).label('category')).where(model.is_active.is_(True)).subquery()
        category = expanded.c.category
        result['categories'] = list(self.db.scalars(select(category).where(func.btrim(category) != '').distinct().order_by(category)))
        return result
