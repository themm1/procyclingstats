from pcs_scraper import Rider

from .scraper_test_base_class import ScraperTestBaseClass


class TestRider(ScraperTestBaseClass):
    ScraperClass = Rider
    
    def test_init(self):
        self.url_ok("rider/tadej-pogacar/")
        self.url_ok("rider/tadej-pogacar/overview/ifqa")
        self.url_ok("rider/tadej-pogacar/2022")
        self.url_ok("rider/tadej-pogacar/2022/overview/")
        
        self.url_not_ok("rider/tadej-pogacar/results")
        self.url_not_ok("rder/tadej-pogacar")
