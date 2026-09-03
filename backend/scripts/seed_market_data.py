import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.business_seed import seed_businesses  # noqa: E402
from app.data.market_seed import seed_market_data  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main() -> None:
    with SessionLocal() as db:
        seed_businesses(db)
        result = seed_market_data(db)
    print("Market demo seed complete.")
    for name, counts in result.items():
        print("{}: {} created, {} updated, {} unchanged".format(name.capitalize(), counts["created"], counts["updated"], counts["unchanged"]))


if __name__ == "__main__":
    main()
