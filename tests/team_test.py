from pcs_scraper import Team

from .scraper_test_base_class import ScraperTestBaseClass


class TestTeam(ScraperTestBaseClass):
    ScraperClass = Team

    def test_init(self):
        self.url_valid("team/bora-hansgrohe-2022/")
        self.url_valid("team/bora-hansgrohe-2022/overview")
        self.url_valid("team/bora-hansgrohe-2022/overview/fewfwe")
        self.url_valid("team/bora-argon-18-2015")
        
        self.url_invalid("team/bora-hansgrohe/")
        self.url_invalid("team/bora-hansgrohe-2022/wins")
        self.url_invalid("tam/bora-hansgrohe-2022/wins")
