import os
import sys

from .race_climbs_scraper import RaceClimbs
from .race_combative_riders_scraper import RaceCombativeRiders
from .race_scraper import Race
from .race_startlist_scraper import RaceStartlist
from .ranking_scraper import Ranking
from .rider_results_scraper import RiderResults
from .rider_scraper import Rider
from .scraper import Scraper
from .stage_scraper import Stage
from .team_scraper import Team

__all__ = [
    "Scraper",
    "RaceClimbs",
    "RaceCombativeRiders",
    "Race",
    "RaceStartlist",
    "Ranking",
    "RiderResults",
    "Rider",
    "Stage",
    "Team"
]

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
