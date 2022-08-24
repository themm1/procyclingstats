from procyclingstats import Ranking

from .scraper_test_base_class import ScraperTestBaseClass


class TestRanking(ScraperTestBaseClass):
    ScraperClass = Ranking

    def test_init(self):
        # ranking URL is every string beggining with rankings
        self.url_valid("rankings")
        self.url_valid("rankingsiiiiii")

        self.url_invalid("ranking")

    def test_eq(self):
        filter_url1 = "rankings.php?date=2021-12-31&nation=&age=&zage=&page=" +\
        "smallerorequal&team=&offset=0&filter=Filter&p=me&s=season-individual"
        filter_url2 = "rankings?date=2021-12-31&p=me&s=season-individual"
        assert Ranking(filter_url1, update_html=False) == Ranking(filter_url2,
            update_html=False)

        assert Ranking("rankings.php", update_html=False) == Ranking(
            "rankings/", update_html=False)

        filter_url3 = filter_url2 + "&nation=be"
        assert Ranking(filter_url1, update_html=False) != Ranking(filter_url3,
            update_html=False)

        assert Ranking("rankings/me", update_html=False) != Ranking("rankings",
            update_html=False)
