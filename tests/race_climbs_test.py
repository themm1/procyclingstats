from procyclingstats import RaceClimbs

from .scraper_test_base_class import ScraperTestBaseClass


class TestRaceClimbs(ScraperTestBaseClass):
    ScraperClass = RaceClimbs

    def test_init(self) -> None:
        self.url_valid("race/tour-de-france/2022/stage-1/stages/climbs-ranked")
        self.url_valid("race/tour-de-france/2022/stages/climbs-ranked")
        self.url_valid("race/tour-de-frances/stages////climbs-ranked")
        self.url_valid("race.php?sorter=steepness&id1=tour-de-france&id2=2022"
            "&id3=stages&id4=climbs-ranked")

        self.url_invalid(
            "race/tour-de-france/2022/stage-1/stages/climbs-ranked/")
        self.url_invalid(
            "race/tour-de-france/2022/stage-1/climbs-ranked")
        self.url_invalid(
            "rce/tour-de-france/2022/stage-1/stages/climbs-ranked")
        self.url_invalid("race.php?sorter=steepness&id1=tour-de-france&"
            "id2=2022&id3=stages&id4=climbs")

    def test_eq(self) -> None:
        self.equal("race/tour-de-france/2022/stages/climbs-ranked",
            "race/tour-de-france/2022/stage-1/stages/climbs-ranked")
        self.equal("race/tour-de-france/2022/stages/climbs-ranked",
            "race//tour-de-france/2022/stage-1/stages/climbs-ranked")

        self.unequal("race/tour-de-france/stages/climbs-ranked",
            "race//tour-de-france/2022/stages/climbs-ranked")
        self.unequal("race/tour-de-france/stages/climbs-ranked",
            "race/tdf/2022/stages/climbs-ranked")
