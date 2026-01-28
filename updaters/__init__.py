# Updaters module
# Each updater should have an update(config) function

from . import scholar_citations
from . import youtube_subscribers
from . import bilibili_stats

UPDATERS = {
    "scholar": scholar_citations,
    "youtube": youtube_subscribers,
    "bilibili": bilibili_stats,
    # Add more updaters here:
    # "github": github_stats,
    # "arxiv": arxiv_papers,
}
