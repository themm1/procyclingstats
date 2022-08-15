import pytest
from pcs_scraper import Startlist

from .scraper_test_base_class import ScraperTestBaseClass


class TestStartlist(ScraperTestBaseClass):
    ScraperClass = Startlist
    
    def test_init(self) -> None:
        self.url_ok("race/tour-de-france/2022/startlist/")
        self.url_ok("race/paris-roubaix/2021/startlist/fga/ak")
        self.url_ok("race/tour-de-france/1970/stage-3b/startlist")
        self.url_ok("race/tour-de-france/2022/gc/startlist/ff")
        self.url_ok("race/tour-de-france/startlist/gggg/ggg")
        
        self.url_not_ok("race/tour-de-france")
        self.url_not_ok("race/tour-de-france/gc/startlist")
        self.url_not_ok("race/tour-de-france/result/startlist")
        self.url_not_ok("race/tour-de-france/2022")
        self.url_not_ok("race/tour-de-france/2022/stage-1")
