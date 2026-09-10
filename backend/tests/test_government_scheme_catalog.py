import csv
from pathlib import Path
import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.government_scheme import GovernmentScheme, VerificationStatus
from app.services.government_scheme_import import HEADERS, import_catalog, normalize, parse_catalog


def row(**changes):
    return dict(dict.fromkeys(HEADERS, ''), scheme_name=' Test योजना ', slug=' TEST Scheme ', details=' महाराष्ट्र ₹500\nSecond line, quoted "text" ', benefits='₹500', eligibility='Resident of Maharashtra', level=' State ', schemeCategory='Agriculture,Rural & Environment, Education & Learning, Education & Learning', tags=' Farmer, Farmer, महिला ', **changes)


def write_csv(tmp_path, rows):
    path = tmp_path / 'fixture.csv'
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_unicode_multiline_artifact_normalization(tmp_path):
    source = row()
    source[''] = 'discard this artifact'
    data, summary = parse_catalog(write_csv(tmp_path, [source]))
    item = data[0]
    assert summary.rows_read == 1
    assert item.details == 'महाराष्ट्र ₹500\nSecond line, quoted "text"'
    assert item.slug == 'test-scheme'
    assert item.scheme_name == 'Test योजना'
    assert item.level == 'STATE' and item.state == 'Maharashtra'
    assert item.categories == ['Agriculture, Rural & Environment', 'Education & Learning']
    assert item.tags == ['Farmer', 'महिला']
    assert item.application_process is None and item.documents_required is None
    assert '' not in item.model_dump()


@pytest.mark.parametrize('level,eligibility,state', [(' central ', 'Maharashtra', None), ('state', 'MAHARASHTRA', 'Maharashtra'), ('State', 'Maharashtra and Gujarat', None), ('State', 'No geographic evidence', None), ('State', 'Resident of Orissa', 'Odisha')])
def test_geography(level, eligibility, state):
    source = row()
    source.update(level=level, eligibility=eligibility)
    assert normalize(source, 'fixture.csv').state == state


def test_duplicates_and_conflicting_slug(tmp_path):
    source = row()
    equivalent = {**source, 'slug': 'test-scheme'}
    data, summary = parse_catalog(write_csv(tmp_path, [source, source, equivalent]))
    assert len(data) == 1 and summary.duplicate_rows_skipped == 2
    data, summary = parse_catalog(write_csv(tmp_path, [source, {**source, 'benefits': 'Different benefit'}]))
    assert not data and summary.conflicts == 2


def test_invalid_rows(tmp_path):
    source = row()
    data, summary = parse_catalog(write_csv(tmp_path, [{**source, 'level': 'Unknown'}, source]))
    assert len(data) == 1 and summary.failed == 1


def test_actual_dataset():
    data, summary = parse_catalog(Path(__file__).resolve().parents[1] / 'data/updated_data.csv')
    assert summary.rows_read == 3400
    assert len(data) == 3397
    assert summary.duplicate_rows_skipped == 3
    assert summary.conflicts == summary.failed == 0
    assert sum(item.level == 'CENTRAL' for item in data) == 541


@pytest.fixture
def catalog_db():
    # Use an isolated PostgreSQL schema, so tests can run BEFORE the local migration.
    from app.db.session import engine
    schema = 'catalog_test_' + uuid.uuid4().hex
    with engine.connect() as connection:
        transaction = connection.begin()
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        GovernmentScheme.__table__.create(connection)
        with Session(bind=connection, join_transaction_mode='create_savepoint') as session:
            yield session
        transaction.rollback()


def test_import_idempotence_dry_run_and_update(catalog_db, tmp_path):
    path = write_csv(tmp_path, [row(), row()])
    assert import_catalog(catalog_db, path, dry_run=True).inserted == 1
    assert catalog_db.scalar(select(GovernmentScheme)) is None
    assert import_catalog(catalog_db, path).inserted == 1
    record = catalog_db.scalar(select(GovernmentScheme))
    assert record.verification_status == VerificationStatus.DATASET_ONLY
    assert record.source_type == 'DATASET'
    assert record.search_vector
    identity, timestamp = record.id, record.updated_at
    assert import_catalog(catalog_db, path).unchanged == 1
    assert record.id == identity and record.updated_at == timestamp
    write_csv(tmp_path, [{**row(), 'benefits': 'Updated ₹600'}])
    assert import_catalog(catalog_db, path, dry_run=True).updated == 1
    catalog_db.refresh(record)
    assert record.benefits == '₹500'
    assert import_catalog(catalog_db, path).updated == 1
    assert record.benefits == 'Updated ₹600'


@pytest.mark.parametrize('status', list(VerificationStatus)[1:])
def test_reviewed_record_protection(catalog_db, tmp_path, status):
    path = write_csv(tmp_path, [row()])
    import_catalog(catalog_db, path)
    record = catalog_db.scalar(select(GovernmentScheme))
    record.verification_status = status
    catalog_db.commit()
    write_csv(tmp_path, [{**row(), 'benefits': 'Unsafe overwrite'}])
    assert import_catalog(catalog_db, path).conflicts == 1
    catalog_db.refresh(record)
    assert record.benefits == '₹500' and record.verification_status == status


def test_fatal_rollback(catalog_db, tmp_path, monkeypatch):
    from app.repositories.government_scheme_repository import GovernmentSchemeRepository
    original = GovernmentSchemeRepository.import_record
    def fail_after_insert(self, data, **kwargs):
        original(self, data, **kwargs)
        self.db.flush()
        raise RuntimeError('injected fatal failure')
    monkeypatch.setattr(GovernmentSchemeRepository, 'import_record', fail_after_insert)
    with pytest.raises(RuntimeError):
        import_catalog(catalog_db, write_csv(tmp_path, [row()]))
    assert catalog_db.scalar(select(GovernmentScheme)) is None


@pytest.mark.parametrize('column,value', [('level', 'INVALID'), ('verification_status', 'INVALID'), ('source_type', 'OFFICIAL'), ('categories', '{}')])
def test_database_constraints(catalog_db, tmp_path, column, value):
    import_catalog(catalog_db, write_csv(tmp_path, [row()]))
    with pytest.raises(IntegrityError):
        catalog_db.execute(text(f'UPDATE government_schemes SET {column} = :value'), {'value': value})
    catalog_db.rollback()


def test_slug_unique(catalog_db, tmp_path):
    path = write_csv(tmp_path, [row()])
    import_catalog(catalog_db, path)
    catalog_db.add(GovernmentScheme(**normalize(row(), path.name).model_dump()))
    with pytest.raises(IntegrityError):
        catalog_db.flush()
    catalog_db.rollback()


def test_validation_failure_preserves_valid_rows(catalog_db, tmp_path):
    summary = import_catalog(catalog_db, write_csv(tmp_path, [row(), {**row(), 'slug': 'bad', 'level': 'Unknown'}]))
    assert summary.inserted == summary.failed == 1
    assert catalog_db.scalar(select(GovernmentScheme)).slug == 'test-scheme'


def test_other_dataset_and_inactive_protection(catalog_db, tmp_path):
    path = write_csv(tmp_path, [row()])
    import_catalog(catalog_db, path)
    record = catalog_db.scalar(select(GovernmentScheme))
    record.is_active = False
    catalog_db.commit()
    write_csv(tmp_path, [{**row(), 'benefits': 'Changed'}])
    assert import_catalog(catalog_db, path).updated == 1
    assert record.is_active is False
    record.source_dataset = 'other.csv'
    catalog_db.commit()
    assert import_catalog(catalog_db, path).conflicts == 1
    assert record.source_dataset == 'other.csv'


def test_bad_csv_rolls_back_before_any_write(catalog_db, tmp_path):
    path = tmp_path / 'malformed.csv'
    path.write_text(','.join(HEADERS) + '\n"unterminated', encoding='utf-8')
    with pytest.raises(csv.Error):
        import_catalog(catalog_db, path)
    assert catalog_db.scalar(select(GovernmentScheme)) is None
    path.write_text('wrong,headers\n', encoding='utf-8')
    with pytest.raises(ValueError, match='headers'):
        import_catalog(catalog_db, path)


def test_migration_upgrade_downgrade():
    import importlib.util
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import inspect
    from app.db.session import engine
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/20260910_12_government_schemes.py'
    spec = importlib.util.spec_from_file_location('catalog_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    with engine.connect() as connection:
        transaction = connection.begin()
        schema = 'catalog_migration_' + uuid.uuid4().hex
        try:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                inspector = inspect(connection)
                assert set(inspector.get_table_names(schema=schema)) == {'government_schemes'}
                assert {c['name'] for c in inspector.get_columns('government_schemes', schema=schema)} == set(GovernmentScheme.__table__.columns.keys())
                assert {i['name'] for i in inspector.get_indexes('government_schemes', schema=schema)} == {i.name for i in GovernmentScheme.__table__.indexes}
                migration.downgrade()
                assert inspect(connection).get_table_names(schema=schema) == []
        finally:
            transaction.rollback()
