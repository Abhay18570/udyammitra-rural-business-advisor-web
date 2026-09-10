import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.business_seed import seed_businesses, seed_baseline_swot  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline-swot-only', action='store_true', help='Update only baseline SWOT on existing businesses.')
    args = parser.parse_args()
    with SessionLocal() as db:
        if args.baseline_swot_only:
            result = seed_baseline_swot(db)
            print('Baseline SWOT seed complete: {updated} updated, {unchanged} unchanged, {missing} missing.'.format(**result))
            return
        result = seed_businesses(db)
    print("Business catalog seed complete: {created} created, {updated} updated, {unchanged} unchanged.".format(**result))


if __name__ == "__main__":
    main()
