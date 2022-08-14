import os
import sys

from pcs import RaceEdition, Ranking, Rider, Scraper, Stage, Startlist, Team
from pcs.__main__ import get_scraper_obj_by_url

from .fixtures_utils import FixturesUtils


class CLI:
    """
    Command line interface for adding and modifiing fixtures.
    example usage: `python -m tests add rider rider/peter-sagan`

    Positional args:
    - `add {url}`: adds parsed data and HTML from the URL to default fixtures
    directory, data are parsed using scraper class for which the URL is valid
    - `add_html {url}`: adds HTML fixture to default fixtures directory
    - `update_htmls`: updates HTMLs of all HTML fixtures in fixtures directory

    Optional args:
    - `-nologging`: turn off logging, defaults to True
    - `-fixtures_path={fixtures_path}`: fixtures directory path, defaults to
    "tests/fixtures/"
    """

    scraper_classes = [
        RaceEdition,
        Startlist,
        Ranking,
        Rider,
        Stage,
        Team
    ]
    command_types = ["add", "add_html", "update_htmls"]
    arg_error = ValueError("Please provide valid arguments, example usage: " + \
        "'python -m tests add rider rider/peter-sagan -nologging " + \
        "-fixtures_path=fixtures/'")

    def __init__(self):
        self.args = sys.argv[1:]
        if not self.args:
            raise self.arg_error
        self.set_command()
        self.set_url()
        self.set_logging()
        self.set_f()
        
    def set_command(self):
        if self.args:
            if self.args[0] not in self.command_types:
                raise self.arg_error
            self.command = self.args[0]

    def set_url(self):
        if len(self.args) >= 2:
            self.url = self.args[1]
        else:
            self.url = None

    def set_logging(self):
        if "-nologging" in self.args:
            self.logging = False
        else:
            self.logging = True
            
    def set_f(self):
        for arg in self.args:
            if "-fixtures_path=" in arg:
                fixtures_path = arg.split("=")[1]
                if not os.path.isdir(fixtures_path):
                    os.mkdir(fixtures_path)
                self.f = FixturesUtils(fixtures_path)
                return
        self.f = FixturesUtils()
        
    def run(self):
        if self.command in ("add", "add_html"):
            ScraperClass = get_scraper_obj_by_url(self.scraper_classes,
                                                  self.url)
            obj = ScraperClass(self.url)
            filename = self.f.url_to_filename(obj.relative_url())

            if self.command == "add":
                if self.logging:
                    print(f"Adding: {filename}.txt")
                self.f.make_html_fixture(obj)
                if self.logging:
                    print(f"Adding: {filename}.json")
                self.f.make_data_fixture(obj)

            elif self.command == "add_html":
                if self.logging:
                    print(f"Adding: {filename}.txt")
                self.f.make_html_fixture(obj)

        elif self.command == "update_htmls":
            urls = self.f.get_urls_from_fixtures_dir("txt")
            for url in urls:
                if self.logging:
                    print(f"Updating: {self.f.url_to_filename(url)}.txt")
                ScraperClass = get_scraper_obj_by_url(self.scraper_classes, url)
                scraper_obj = ScraperClass(url)
                self.f.make_html_fixture(scraper_obj)
        else:
            raise self.arg_error

if __name__ == "__main__":
    cli = CLI()
    cli.run()
