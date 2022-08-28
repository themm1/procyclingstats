from procyclingstats import RiderResults

from .scraper_test_base_class import ScraperTestBaseClass


class TestRiderResults(ScraperTestBaseClass):
    ScraperClass = RiderResults

    def test_init(self):
        self.url_valid("rider.php?anything")
        self.url_valid("rider/tadej-pogacar/results/")
        self.url_valid("rider/tadej-pogacar/results/ggff")

        self.url_invalid("rider.php")
        self.url_invalid("rider/tadej-pogacar/re/")
        self.url_invalid("rider/tadej-pogacar/final-5k-analysis")

    def test_eq(self):
        filter_url1 = ("rider.php?xseason=2022&zxseason=&pxseason=equal&sort" +
        "=date&race=&km1=&zkm1=&pkm1=equal&limit=100&offset=0&topx=&ztopx=" +
        "&ptopx=smallerorequal&type=&znation=&continent=&pnts=&zpnts=&ppnts=" +
        "equal&level=&rnk=&zrnk=&prnk=equal&exclude_tt=0&racedate=&zracedate" +
        "=&pracedate=equal&name=&pname=contains&category=&profile_score=" +
        "&zprofile_score=&pprofile_score=largerorequal&filter=Filter&id=" +
        "alexander-kristoff&p=results&s=all")

        filter_url2 = ("rider.php?xseason=2022&pxseason=equal&sort=date" +
        "&pkm1=equal&limit=100&ptopx=smallerorequal&ppnts=equal&prnk=equal" +
        "&exclude_tt=0&pracedate=equal&pname=contains&pprofile_score=" +
        "largerorequal&id=alexander-kristoff&p=results&s=all")
        self.equal(filter_url1, filter_url2)
        self.equal("rider/alberto-contador/results/ggff/",
                   "rider/alberto-contador/results")

        self.unequal(filter_url1, filter_url2 + "&type=2")
        self.unequal("rider/alberto-contador/results",
                     "rider/alberto-contador/results/final-5k-analysis")
