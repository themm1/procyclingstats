from pcs_scraper import RaceEdition

from .scraper_test_base_class import ScraperTestBaseClass


class TestRaceEdition(ScraperTestBaseClass):
    ScraperClass = RaceEdition
    
    def test_init(self):
        self.url_ok("race/tour-de-france/2022/overview/")
        self.url_ok("race/paris-roubaix/2021/overview/fga/ak")
        self.url_ok("race/tour-de-france/2022/stage-3/overview/ff")
        self.url_ok("race/tour-de-france/2022/gc/overview/")
        self.url_ok("race/tour-de-france/overview/gggg/ggg")
        
        self.url_not_ok("race/tour-de-france")
        self.url_not_ok("race/tour-de-france/gc/overview")
        self.url_not_ok("race/tour-de-france/result/overview")
        self.url_not_ok("race/tour-de-france/2022")
        self.url_not_ok("race/tour-de-france/2022/stage-1")
