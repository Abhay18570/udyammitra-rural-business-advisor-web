"""Run mocked tests in a disposable schema, retaining development data.

Requires the existing migrated local PostGIS database (including migration 09's
immutability function). Never supplies or prints credentials. Run from backend:
    .venv/bin/python scripts/run_module14_tests.py [pytest paths]
"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.db.base import Base
import app.models
import app.db.session as sessions
import pytest
schema = 'module14_test_' + uuid.uuid4().hex
admin = create_engine(get_settings().database_url)
engine = None
try:
    with admin.begin() as connection:
        connection.execute(text('CREATE SCHEMA "' + schema + '"'))
    engine = create_engine(get_settings().database_url, connect_args={'options':'-csearch_path='+schema+',public'}, execution_options={'schema_translate_map':{None:schema}})
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TRIGGER immutable_business_analysis BEFORE UPDATE ON business_analyses FOR EACH ROW EXECUTE FUNCTION public.reject_business_analysis_update()"))
    sessions.engine = engine
    sessions.SessionLocal.configure(bind=engine)
    from app.data.business_seed import seed_businesses
    from app.data.market_seed import seed_market_data
    with sessions.SessionLocal() as db:
        seed_businesses(db)
        seed_market_data(db)
    code=pytest.main(sys.argv[1:]+['-q','--tb=short'])
except Exception as exc:
    print('Isolated test setup failed:',type(exc).__name__)
    code=2
finally:
    if engine is not None: engine.dispose()
    with admin.begin() as connection:
        connection.execute(text('DROP SCHEMA "'+schema+'" CASCADE'))
    admin.dispose()
sys.exit(code)
