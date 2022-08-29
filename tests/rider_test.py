from procyclingstats import Rider

from .scraper_test_base_class import ScraperTestBaseClass


class TestRider(ScraperTestBaseClass):
    ScraperClass = Rider

    def test_init(self) -> None:
        self.url_valid("rider/tadej-pogacar/")
        self.url_valid("rider/tadej-pogacar/overview/ifqa")
        self.url_valid("rider/tadej-pogacar/2022")
        self.url_valid("rider/tadej-pogacar/2022/overview/")

        self.url_invalid("rider/tadej-pogacar/results")
        self.url_invalid("rder/tadej-pogacar")

    def test_eq(self):
        self.equal("rider/tadej-pogacar", "rider/tadej-pogacar/overview/")
        self.unequal("rider/tadej-pogacar", "rider/tadej-pog")
