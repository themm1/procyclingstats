from pcs_scraper import Stage

from .scraper_test_base_class import ScraperTestBaseClass


class TestStage(ScraperTestBaseClass):
    ScraperClass = Stage

    def test_init(self):
        self.url_ok("race/tour-de-france/")
        self.url_ok("race/paris-roubaix/2021/result")
        self.url_ok("race/okolo-slovenska/2021/prologue")
        self.url_ok("race/okolo-slovenska/2021/prologue/result/fg")
        self.url_ok("race/tour-de-france/result/ffa/")
        
        self.url_not_ok("race/tour-de-france/overview/result")
        self.url_not_ok("race/tour-de-france/2022/startlist/result")
        self.url_not_ok("rce/tour-de-france/")
        self.url_not_ok("race/2022")
        self.url_not_ok("race/tour-de-france/222")
