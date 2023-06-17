from procyclingstats import (Race, RaceClimbs, RaceStartlist, Ranking, Rider,
                             RiderResults, Stage, Team)

from .scraper_test_base_class import ScraperTestBaseClass


class TestRaceClimbs(ScraperTestBaseClass):
    ScraperClass = RaceClimbs
    
class TestStage(ScraperTestBaseClass):
    ScraperClass = Stage   

class TestStartlist(ScraperTestBaseClass):
    ScraperClass = RaceStartlist
    
class TestRanking(ScraperTestBaseClass):
    ScraperClass = Ranking

class TestRider(ScraperTestBaseClass):
    ScraperClass = Rider
   
class TestRiderResults(ScraperTestBaseClass):
    ScraperClass = RiderResults

class TestTeam(ScraperTestBaseClass):
    ScraperClass = Team

class TestRace(ScraperTestBaseClass):
    ScraperClass = Race

