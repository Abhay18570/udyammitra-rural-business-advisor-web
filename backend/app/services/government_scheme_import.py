"""Deterministic CSV ingestion only; source prose is not eligibility logic."""
from typing import Optional
import csv
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.repositories.government_scheme_repository import GovernmentSchemeRepository
from app.schemas.government_scheme import GovernmentSchemeImport

HEADERS = ['scheme_name', 'slug', 'details', 'benefits', 'eligibility', 'application', 'documents', 'level', 'schemeCategory', '', 'tags']
STATES = ('Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry')
ALIASES = {state: [state] for state in STATES}
ALIASES['Odisha'] += ['Orissa']
ALIASES['Puducherry'] += ['Pondicherry']
ALIASES['Uttarakhand'] += ['Uttaranchal']
ALIASES['Jammu and Kashmir'] += ['Jammu & Kashmir']
ALIASES['Andaman and Nicobar Islands'] += ['Andaman & Nicobar Islands']
ALIASES['Dadra and Nagar Haveli and Daman and Diu'] += ['Dadra and Nagar Haveli', 'Daman and Diu', 'Dadra & Nagar Haveli', 'Daman & Diu']
STATE_PATTERNS = {state: re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(a) for a in aliases) + r')(?!\w)', re.I) for state, aliases in ALIASES.items()}


@dataclass
class ImportSummary:
    rows_read: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    duplicate_rows_skipped: int = 0
    conflicts: int = 0
    failed: int = 0
    issues: list[str] = field(default_factory=list)

    def counts(self):
        return {key: value for key, value in asdict(self).items() if key != 'issues'}


def prose(value: str) -> Optional[str]:
    # Preserve internal spacing, line breaks, bullets, currency and Unicode.
    return value.replace('\ufeff', '').replace('\r\n', '\n').replace('\r', '\n').strip() or None


def compact(value: str) -> str:
    return ' '.join((prose(value) or '').split())


def list_values(value: str, *, categories: bool = False) -> list[str]:
    # The taxonomy itself contains commas; keep those known category labels whole.
    if categories:
        for label in ('Agriculture,Rural & Environment', 'Agriculture, Rural & Environment', 'Banking,Financial Services & Insurance', 'Banking, Financial Services & Insurance', 'Science,IT & Communications', 'Science, IT & Communications'):
            value = value.replace(label, label.replace(',', '\x1f'))
    result, seen = [], set()
    for item in value.split(','):
        item = compact(item.replace('\x1f', ', '))
        if item and item.casefold() not in seen:
            result.append(item)
            seen.add(item.casefold())
    return result


def extract_state(row: dict, level: str) -> Optional[str]:
    if level != 'STATE':
        return None
    # A unique geographic mention is a discovery hint, not verified jurisdiction.
    text = ' '.join(compact(row[key]) for key in ('scheme_name', 'details', 'eligibility', 'application'))
    matches = [state for state, pattern in STATE_PATTERNS.items() if pattern.search(text)]
    return matches[0] if len(matches) == 1 else None


def normalize(row: dict, dataset: str) -> GovernmentSchemeImport:
    level = compact(row['level']).upper()
    return GovernmentSchemeImport(
        scheme_name=compact(row['scheme_name']),
        slug=re.sub(r'\s+', '-', compact(row['slug']).lower()),
        details=prose(row['details']), benefits=prose(row['benefits']), eligibility=prose(row['eligibility']),
        application_process=prose(row['application']), documents_required=prose(row['documents']),
        level=level, state=extract_state(row, level), categories=list_values(row['schemeCategory'], categories=True),
        tags=list_values(row['tags']), source_dataset=dataset,
    )


def parse_catalog(path: Path) -> tuple[list[GovernmentSchemeImport], ImportSummary]:
    summary = ImportSummary()
    records, blocked, exact = {}, set(), set()
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != HEADERS:
            raise ValueError('Unexpected CSV headers')
        for number, row in enumerate(reader, start=2):
            summary.rows_read += 1
            if None in row or any(value is None for value in row.values()):
                summary.failed += 1
                summary.issues.append(f'Row {number}: invalid column count')
                continue
            # Empty artifact column intentionally ignored; never persisted.
            fingerprint = tuple(row[key] for key in HEADERS if key)
            if fingerprint in exact:
                summary.duplicate_rows_skipped += 1
                continue
            exact.add(fingerprint)
            try:
                data = normalize(row, path.name)
            except (ValueError, ValidationError):
                summary.failed += 1
                summary.issues.append(f'Row {number}: invalid catalog fields')
                continue
            if data.slug in blocked:
                summary.conflicts += 1
                summary.issues.append(f'Row {number}: conflicting slug {data.slug}')
            elif data.slug in records:
                if records[data.slug] == data:
                    summary.duplicate_rows_skipped += 1
                else:
                    # Quarantine ALL versions; never choose the first conflicting row.
                    del records[data.slug]
                    blocked.add(data.slug)
                    summary.conflicts += 2
                    summary.issues.append(f'Row {number}: conflicting slug {data.slug}; all versions excluded')
            else:
                records[data.slug] = data
    return list(records.values()), summary


def import_catalog(db: Session, path: Path, *, dry_run: bool = False) -> ImportSummary:
    try:
        records, summary = parse_catalog(path)
        repository = GovernmentSchemeRepository(db)
        for data in records:
            outcome = repository.import_record(data, dry_run=dry_run)
            setattr(summary, outcome, getattr(summary, outcome) + 1)
            if outcome == 'conflicts':
                summary.issues.append(f'Protected record: {data.slug}')
        if dry_run:
            db.rollback()
        else:
            db.commit()
        return summary
    except Exception:
        db.rollback()
        raise
