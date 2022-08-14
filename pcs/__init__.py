import os
import sys

from .race_edition_scraper import RaceEdition
from .ranking_scraper import Ranking
from .rider_scraper import Rider
from .scraper import Scraper
from .stage_scraper import Stage
from .startlist_scraper import Startlist
from .team_scraper import Team

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
