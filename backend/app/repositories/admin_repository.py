from sqlalchemy import case, distinct, func, or_, select, tuple_
from sqlalchemy.orm import Session

from app.models.business import BusinessProfile
from app.models.profile import EntrepreneurProfile
from app.schemas.admin import EntrepreneurFilters
from app.models.user import User, UserRole


def clean_location(column):
    return func.nullif(func.trim(func.regexp_replace(column, r'\s+', ' ', 'g')), '')


def normalized_location(column):
    return func.lower(clean_location(column))


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def overview(self) -> dict[str, int]:
        profile = EntrepreneurProfile
        # Canonical comparison only; do not rewrite users' saved location names.
        state = normalized_location(profile.state)
        district = normalized_location(profile.district)
        statement = select(
            func.count(User.id).label('total_registered_users'),
            func.count(profile.id).label('total_entrepreneurs'),
            func.count(User.id).filter(profile.id.is_(None)).label('profiles_pending'),
            func.count(profile.id).filter(profile.has_existing_business.is_(False)).label('new_enterprises'),
            func.count(profile.id).filter(profile.has_existing_business.is_(True)).label('existing_enterprises'),
            func.count(distinct(state)).label('states_count'),
            func.count(distinct(tuple_(state, district))).filter(state.is_not(None), district.is_not(None)).label('districts_count'),
        ).select_from(User).outerjoin(profile, profile.user_id == User.id).where(User.role == UserRole.USER)
        return dict(self.db.execute(statement).mappings().one())

    def geographic_groups(self, state=None):
        p = EntrepreneurProfile
        column = p.state if state is None else p.district
        key = normalized_location(column)
        query = select(
            key.label('key'), func.min(clean_location(column)).label('name'),
            func.count().label('entrepreneur_count'),
            func.count().filter(p.has_existing_business.is_(False)).label('new_enterprises'),
            func.count().filter(p.has_existing_business.is_(True)).label('existing_enterprises'),
            func.count(distinct(normalized_location(p.district))).label('districts_count'),
        ).select_from(p).join(User, User.id == p.user_id).where(User.role == UserRole.USER)
        if state is not None:
            query = query.where(normalized_location(p.state) == normalized_location(state))
        grouped = query.group_by(key).subquery()
        summary = self.db.execute(select(
            func.coalesce(func.sum(grouped.c.entrepreneur_count), 0).label('total_entrepreneurs'),
            func.coalesce(func.sum(grouped.c.entrepreneur_count).filter(grouped.c.key.is_(None)), 0).label('missing_count'),
            func.count(grouped.c.key).label('locations_count'),
            func.coalesce(func.sum(grouped.c.districts_count).filter(grouped.c.key.is_not(None)), 0).label('districts_count'),
            func.coalesce(func.sum(grouped.c.new_enterprises), 0).label('new_enterprises'),
            func.coalesce(func.sum(grouped.c.existing_enterprises), 0).label('existing_enterprises'),
        )).mappings().one()
        rows = self.db.execute(select(grouped).where(grouped.c.key.is_not(None)).order_by(grouped.c.entrepreneur_count.desc(), grouped.c.key)).mappings().all()
        return dict(summary), [dict(row) for row in rows]

    def state_name(self, state):
        p = EntrepreneurProfile
        key = normalized_location(p.state)
        return self.db.execute(select(func.min(clean_location(p.state)).label('name'), key.label('key')).join(User, User.id == p.user_id)
                               .where(User.role == UserRole.USER, key == normalized_location(state))
                               .group_by(key)).mappings().first()

    def list_entrepreneurs(self, filters: EntrepreneurFilters):
        p, b = EntrepreneurProfile, BusinessProfile
        query = select(
            User.full_name, User.email, User.mobile_number, User.preferred_language, User.created_at,
            p.state, p.district, p.taluka, p.village, b.name.label('proposed_business'),
            case((p.has_existing_business.is_(True), 'existing'), (p.has_existing_business.is_(False), 'new'), else_='unspecified').label('enterprise_status'),
            case((p.id.is_(None), 'pending'), (p.onboarding_completed.is_(True), 'complete'), else_='created').label('profile_status'),
        ).select_from(User).outerjoin(p, p.user_id == User.id).outerjoin(b, b.id == p.proposed_business_id).where(User.role == UserRole.USER)
        for field in ('state', 'district'):
            value = getattr(filters, field)
            if value and value.strip():
                query = query.where(normalized_location(getattr(p, field)) == normalized_location(value))
        if filters.enterprise_status:
            value = {'new': False, 'existing': True, 'unspecified': None}[filters.enterprise_status]
            query = query.where(p.has_existing_business.is_(value))
        if filters.business_slug:
            query = query.where(b.slug == filters.business_slug)
        if filters.search and filters.search.strip():
            # Escape LIKE metacharacters so searches are literal substrings.
            value = filters.search.strip().replace('\\', '\\\\').replace('%', r'\%').replace('_', r'\_')
            query = query.where(or_(*(column.ilike('%' + value + '%', escape='\\') for column in
                                    (User.full_name, User.email, User.mobile_number, p.village, p.district, p.state, b.name))))
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        order = User.created_at.asc() if filters.sort == 'created_asc' else User.created_at.desc()
        rows = self.db.execute(query.order_by(order, User.id).limit(filters.page_size).offset((filters.page - 1) * filters.page_size)).mappings().all()
        return dict(items=[dict(row) for row in rows], total=total, page=filters.page, page_size=filters.page_size,
                    total_pages=(total + filters.page_size - 1) // filters.page_size)
