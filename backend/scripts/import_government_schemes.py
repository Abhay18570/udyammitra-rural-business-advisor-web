"""Run from any directory; use the existing application settings and session."""
import argparse
import os
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Report projected changes without writing to PostgreSQL')
    parser.add_argument('--file', type=Path, default=BACKEND / 'data' / 'updated_data.csv')
    args = parser.parse_args()
    # Resolve explicit relative paths before changing directory for existing .env loading.
    path = args.file.resolve()
    os.chdir(BACKEND)
    try:
        from app.db.session import SessionLocal
        from app.services.government_scheme_import import import_catalog
        with SessionLocal() as db:
            summary = import_catalog(db, path, dry_run=args.dry_run)
    except Exception as exc:
        # DB exceptions may embed credentials, SQL parameters and full descriptions.
        print(f'Import aborted ({type(exc).__name__}); transaction rolled back. No changes committed.', file=sys.stderr)
        return 1
    print('Government Schemes Import' + (' (dry run; projected counts)' if args.dry_run else ''))
    print('--------------------------')
    for key, value in summary.counts().items():
        print(f'{key}: {value}')
    for issue in summary.issues[:20]:
        print(issue)
    if len(summary.issues) > 20:
        print(f'{len(summary.issues) - 20} additional issues omitted')
    return 1 if summary.failed or summary.conflicts else 0


if __name__ == '__main__':
    raise SystemExit(main())
