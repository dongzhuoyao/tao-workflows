# tao-workflows

Automated data fetchers powered by GitHub Actions. Runs daily cron jobs to fetch and store data that can be read anytime.

## Features

- **Daily automated updates** via GitHub Actions cron
- **Modular design** - easily add new data fetchers
- **Data stored in YAML** - easy to read and use in other projects

## Available Updaters

| Updater | Description | Output |
|---------|-------------|--------|
| `scholar` | Google Scholar citations | `data/scholar_citations.yml` |

## Setup

### 1. Configure

Edit `config.yml` with your settings:

```yaml
scholar:
  user_id: "YOUR_GOOGLE_SCHOLAR_ID"  # Find this in your Scholar profile URL
  output_file: "data/scholar_citations.yml"
```

**How to find your Google Scholar ID:**
1. Go to [Google Scholar](https://scholar.google.com)
2. Click on your profile
3. Look at the URL: `https://scholar.google.com/citations?user=XXXXXXXXXX`
4. The `XXXXXXXXXX` part is your user ID

### 2. Run locally (optional)

```bash
pip install -r requirements.txt
python main.py           # Run all updaters
python main.py scholar   # Run specific updater
```

### 3. Enable GitHub Actions

Push to GitHub and the workflow will:
- Run daily at 6:00 AM UTC
- Commit updated data back to the repo

You can also trigger manually: **Actions** → **Daily Data Update** → **Run workflow**

## Reading Data

### From another repo (e.g., your website)

Fetch the raw YAML file:

```python
import yaml
import urllib.request

url = "https://raw.githubusercontent.com/YOUR_USERNAME/tao-workflows/main/data/scholar_citations.yml"
with urllib.request.urlopen(url) as f:
    data = yaml.safe_load(f)
    print(f"Total citations: {data['metadata']['total_citations']}")
```

### In Jekyll (al-folio theme)

Add to your `_data` folder or fetch during build:

```yaml
# In _config.yml, you can reference external data
# Or use a build step to fetch the YAML file
```

## Adding New Updaters

1. Create `updaters/your_updater.py`:

```python
def update(config: dict) -> bool:
    """
    Fetch data and save to file.

    Args:
        config: Dictionary from config.yml

    Returns:
        True if updated, False if skipped
    """
    output_file = config.get("output_file", "data/your_data.yml")

    # Your fetch logic here
    data = {"key": "value"}

    # Save to file
    with open(output_file, "w") as f:
        yaml.dump(data, f)

    return True
```

2. Register in `updaters/__init__.py`:

```python
from . import your_updater

UPDATERS = {
    "scholar": scholar_citations,
    "your_updater": your_updater,  # Add this
}
```

3. Add config in `config.yml`:

```yaml
your_updater:
  some_setting: "value"
  output_file: "data/your_data.yml"
```

## Output Format

### Scholar Citations (`data/scholar_citations.yml`)

```yaml
metadata:
  last_updated: "2024-01-27"
  scholar_id: "your_id"
  total_citations: 1234
  paper_count: 42

papers:
  abc123xyz:
    title: "Your Paper Title"
    year: "2024"
    citations: 100
  def456uvw:
    title: "Another Paper"
    year: "2023"
    citations: 50
```

## License

MIT
