from pcs_scraper import Ranking

from .scraper_test_base_class import ScraperTestBaseClass


class TestRanking(ScraperTestBaseClass):
    ScraperClass = Ranking
    
    def test_init(self):
        # ranking URL is every string beggining with rankings
        self.url_ok("rankings")
        self.url_ok("rankingsiiiiii")

        self.url_not_ok("ranking")
