import os
import sys

from .race_scraper import Race
from .race_startlist_scraper import RaceStartlist
from .ranking_scraper import Ranking
from .rider_results_scraper import RiderResults
from .rider_scraper import Rider
from .scraper import Scraper
from .stage_scraper import Stage
from .team_scraper import Team

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
