# tao-workflows

Automated data collection system using GitHub Actions cron jobs. Fetches academic and social platform stats daily.

## Architecture

- **Entry point**: `main.py` — loads `config.yml`, dispatches to updaters
- **Updaters**: `updaters/` — each module has `update(config: dict) -> bool`
- **Data**: `data/` — YAML files with timestamped history
- **CI**: `.github/workflows/daily-update.yml` — daily cron at 6 AM UTC

## Adding a New Updater

1. Create `updaters/new_name.py` with `def update(config: dict) -> bool`
2. Register in `updaters/__init__.py`
3. Add config section in `config.yml`

## Conventions

- Use `logging` module (not `print()`). Each module: `logger = logging.getLogger(__name__)`
- Network calls should use `tenacity` retry decorators for resilience
- Each updater checks idempotency (skip if already updated today)
- Return `True` if data was updated, `False` if skipped/failed
- Output YAML files go in `data/` with `metadata.last_updated` field
- `data/scheduler_status.yml` is gitignored (high-frequency local updates)

## Running Locally

```bash
pip install -r requirements.txt
python main.py              # all updaters
python main.py bilibili     # single updater
```

## Secrets (GitHub Actions)

- `RESEND_API_KEY` — email notifications on failure
