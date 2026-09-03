import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.business_seed import seed_businesses  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main() -> None:
    with SessionLocal() as db:
        result = seed_businesses(db)
    print("Business catalog seed complete: {created} created, {updated} updated, {unchanged} unchanged.".format(**result))


if __name__ == "__main__":
    main()
