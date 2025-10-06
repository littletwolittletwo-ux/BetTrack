# Test Suite (bet-ocr-app)

## Prereqs
1) App is running on Replit (uvicorn at port 8000).
2) Database migrated and seeded:
   - `alembic upgrade head`
   - `python scripts/create_defaults.py`
3) Upload the sample screenshot into the repo at:
   `tests/samples/sportsbet_sample.png`
   (Use the file provided by the assistant.)

## Install test deps

```bash
pip install -r requirements-test.txt
```

## Run tests

```bash
pytest -q
```

## Quick smoke

```bash
bash scripts/smoke.sh
```

## Notes
- Default logins (dev only):
  - admin / dwang1237
  - slave / admin
- The upload test posts `set_id`, `bookmaker_name`, `stake_manual`, and the screenshot; it then verifies parsed values and computed `profit` follow rules.