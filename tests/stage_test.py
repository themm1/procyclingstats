from procyclingstats import Stage

from .scraper_test_base_class import ScraperTestBaseClass


class TestStage(ScraperTestBaseClass):
    ScraperClass = Stage

    def test_init(self) -> None:
        self.url_valid("race/paris-roubaix/2021/result")
        self.url_valid("race/okolo-slovenska/2021/prologue")
        self.url_valid("race/okolo-slovenska/2021/prologue/result/fg")
        self.url_valid("race/paris-roubaix/2021/result/result/fff")
        self.url_valid("race/e3-harelbeke/2019/result/")

        self.url_invalid("race/tour-de-france/overview/result")
        self.url_invalid("race/tour-de-france/2022/startlist/result")
        self.url_invalid("rce/tour-de-france/")
        self.url_invalid("race/tour-de-france/result/")
        self.url_invalid("race/tour-de-france/222")

    def test_eq(self) -> None:
        self.equal("race/tour-de-france/2022/stage-18/result/fff",
                   "race/tour-de-france/2022/stage-18")

        self.unequal("race/tdf/2022/stage-1",
                     "race/tour-de-france/2022/stage-1")
        self.unequal("race/okolo-slovenska/2021/prologue",
                     "race/okolo-slovenska/2021/gc")
