# Updaters module
# Each updater should have an update(config) function

from . import scholar_citations

UPDATERS = {
    "scholar": scholar_citations,
    # Add more updaters here:
    # "github": github_stats,
    # "arxiv": arxiv_papers,
}
