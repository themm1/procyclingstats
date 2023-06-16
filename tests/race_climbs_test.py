from procyclingstats import RaceClimbs

from .scraper_test_base_class import ScraperTestBaseClass


class TestRaceClimbs(ScraperTestBaseClass):
    ScraperClass = RaceClimbs

    def test_init(self) -> None:
        self.url_valid("race/tour-de-france/2022/route/climbs//")
        self.url_valid("race/tour-de-france/2021/route//climbs")

        self.url_invalid("race/tour-de-france/2022/stage-21/route/climbs/")
        self.url_invalid("rac/tour-de-france/2022/route/climbs/")

    def test_eq(self) -> None:
        self.equal("race/tour-de-france/2022/route/climbs//",
            "race/tour-de-france/2022/route//climbs")

        self.unequal("race/tour-de-france/2021/route/climbs",
            "race/tour-de-france/2022/route/climbs")
