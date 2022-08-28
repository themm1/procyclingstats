"""
procyclingstats package
~~~~~~~~~~~~~~~~~~~~~

Procyclingstats is a package for scraping https://www.procyclingstats.com/.
Interface consists from scraping classes which are currently Race,
RaceStartlist, Ranking, Rider, RiderResults, Stage and Team.

Basic Rider class usage:
    >>> from procyclingstats import Rider
    >>> rider = Rider("rider/tadej-pogacar")
    >>> rider.birthdate()
    "1998-9-21"
    >>> rider.parse()
    {
        'birthdate': '1998-9-21',
        'height': 1.76,
        'name': 'Tadej  Pogačar',
        'nationality': 'SI',
        ...
    }

Usage of all scraping classes is almost the same and the only difference among
them are parsing method as is for example `birthdate` in Rider usage example.

More information at https://github.com/themm1/procyclingstats.
"""


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

__all__ = [
    "Scraper",
    "Race",
    "RaceStartlist",
    "Ranking",
    "RiderResults",
    "Rider",
    "Stage",
    "Team"
]

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
