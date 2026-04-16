# tao-workflows

Automated daily data collection for academic and social platform stats, powered by GitHub Actions.

## Available Updaters

| Updater | Source | Output |
|---------|--------|--------|
| `scholar` | Google Scholar | `data/scholar_citations.yml` |
| `youtube` | YouTube (via yt-dlp) | `data/youtube_subscribers.yml` |
| `bilibili` | Bilibili API | `data/bilibili_stats.yml` |

## Setup

### 1. Configure

Edit `config.yml` with your settings:

```yaml
scholar:
  user_id: "YOUR_GOOGLE_SCHOLAR_ID"
youtube:
  channel: "@your_handle"
bilibili:
  mid: "YOUR_USER_ID"
```

### 2. Run locally

```bash
pip install -r requirements.txt
python main.py              # Run all updaters
python main.py scholar      # Run specific updater
python main.py youtube bilibili  # Run multiple
```

### 3. GitHub Actions

Push to GitHub and the workflow will:
- Run daily at 6:00 AM UTC
- Commit updated data back to the repo
- Send email notification on failure (via Resend)

Manual trigger: **Actions** > **Daily Data Update** > **Run workflow**

## Adding New Updaters

1. Create `updaters/your_updater.py`:

```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

def update(config: dict) -> bool:
    """Fetch data and save to file. Return True if updated."""
    # Your fetch logic here
    return True
```

2. Register in `updaters/__init__.py`
3. Add config in `config.yml`

## Data Format

All data files use YAML with a consistent structure:

```yaml
metadata:
  last_updated: "2026-01-30"
  # ... source-specific metadata
history:          # (youtube/bilibili)
  "2026-01-28":
    subscribers: 178
papers:           # (scholar)
  paper_id:
    title: "Paper Title"
    citations: 100
```

## GitHub Actions Secrets

| Secret | Purpose |
|--------|---------|
| `RESEND_API_KEY` | Email failure notifications |

## License

MIT
