from procyclingstats import RaceStartlist

from .scraper_test_base_class import ScraperTestBaseClass


class TestStartlist(ScraperTestBaseClass):
    ScraperClass = RaceStartlist

    def test_init(self) -> None:
        self.url_valid("race/tour-de-france/2022/startlist/")
        self.url_valid("race/paris-roubaix/2021/startlist/fga/ak")
        self.url_valid("race/tour-de-france/1970/stage-3b/startlist")
        self.url_valid("race/tour-de-france/2022/gc/startlist/ff")
        self.url_valid("race/tour-de-france/startlist/gggg/ggg")
        self.url_valid("race/cyclassics-hamburg/2022/result/startlist/feef")

        self.url_invalid("race/tour-de-france")
        self.url_invalid("race/tour-de-france/gc/startlist")
        self.url_invalid("race/tour-de-france/result/startlist")
        self.url_invalid("race/tour-de-france/2022")
        self.url_invalid("race/tour-de-france/2022/stage-1")
        self.url_invalid("race/cyclassics-hamburg/2022/result/gggg")

