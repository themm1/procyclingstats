from procyclingstats import Ranking

from .scraper_test_base_class import ScraperTestBaseClass


class TestRanking(ScraperTestBaseClass):
    ScraperClass = Ranking

    def test_init(self):
        # ranking URL is every string beggining with rankings
        self.url_valid("rankings")
        self.url_valid("rankingsiiiiii")

        self.url_invalid("ranking")
