from procyclingstats import Race

from .scraper_test_base_class import ScraperTestBaseClass


class TestRace(ScraperTestBaseClass):
    ScraperClass = Race

    def test_init(self) -> None:
        self.url_valid("race/tour-de-france/2022/overview/")
        self.url_valid("race/tour-de-france/2022/stats/")
        self.url_valid("race/paris-roubaix/2021/overview/fga/ak")

        self.url_invalid("race/tour-de-france")
        self.url_invalid("race/tour-de-france/gc/overview")

    def test_eq(self) -> None:
        self.equal("race/tour-de-france/2022",
                   "race/tour-de-france/2022/overview/ggff/")

        self.unequal("race/tour-de-france/2022/overview",
                     "race/tour-de-france/2010/overview")
