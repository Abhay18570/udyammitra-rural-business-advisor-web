from sqlalchemy.orm import Session

from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import AdminOverview


class AdminService:
    def __init__(self, db: Session):
        self.repository = AdminRepository(db)

    def overview(self) -> AdminOverview:
        return AdminOverview.model_validate(self.repository.overview())

    def states(self):
        from app.schemas.admin import StateAnalytics
        summary, rows = self.repository.geographic_groups()
        valid = int(summary['total_entrepreneurs'] - summary['missing_count'])
        return StateAnalytics(
            total_entrepreneurs=summary['total_entrepreneurs'], located_entrepreneurs=valid,
            missing_state_count=summary['missing_count'], states_count=summary['locations_count'],
            districts_count=summary['districts_count'],
            states=[dict(state=row['name'], state_key=row['key'], percentage=percentage(row['entrepreneur_count'], valid), **{k:row[k] for k in ('entrepreneur_count','districts_count','new_enterprises','existing_enterprises')}) for row in rows],
        )

    def districts(self, state):
        from fastapi import HTTPException
        from app.schemas.admin import DistrictAnalytics
        if len(state) > 100:
            raise HTTPException(status_code=404, detail='State not found.')
        name = self.repository.state_name(state)
        if name is None:
            raise HTTPException(status_code=404, detail='State not found.')
        summary, rows = self.repository.geographic_groups(state)
        valid = int(summary['total_entrepreneurs'] - summary['missing_count'])
        return DistrictAnalytics(
            state=name['name'], state_key=name['key'], total_entrepreneurs=summary['total_entrepreneurs'],
            districts_count=summary['locations_count'], missing_district_count=summary['missing_count'],
            new_enterprises=summary['new_enterprises'], existing_enterprises=summary['existing_enterprises'],
            districts=[dict(district=row['name'], district_key=row['key'], percentage=percentage(row['entrepreneur_count'], valid), **{k:row[k] for k in ('entrepreneur_count','new_enterprises','existing_enterprises')}) for row in rows],
        )

    def entrepreneurs(self, filters):
        from app.schemas.admin import EntrepreneurPage
        return EntrepreneurPage.model_validate(self.repository.list_entrepreneurs(filters))


def percentage(count, total):
    from decimal import Decimal, ROUND_HALF_UP
    return format((Decimal(count) * 100 / Decimal(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f') if total else '0.00'
